% Symbolic Explainable Artificial Intelligence
% GROUP 18:
% Artur Krystopchuk (104145)
% Sofia Ligeiro (116046)
%
% Alien Tiles (CSPLib 027): find how many times to click each square so that
% the all-zero board becomes `goal_board`, using as few clicks as possible.

% ================================================================ Instance
int: board_size;
int: number_of_colours;
array[1..board_size, 1..board_size] of 0..number_of_colours-1: goal_board;

% Turns symmetry breaking on or off (on by default). Only needed to measure
% how much it helps; normal runs leave it unset.
opt bool: break_symmetries;
bool: use_symmetry_breaking = break_symmetries default true;

% ================================================================ Variables
array[1..board_size, 1..board_size] of var 0..number_of_colours-1: clicks_per_square;

% Total clicks in each row / each column, taken mod number_of_colours.
% These totals are all that matters for the final colours, so the solver
% decides them first and the clicks on each square follow automatically.
array[1..board_size] of var 0..number_of_colours-1: row_clicks_mod_colours;
array[1..board_size] of var 0..number_of_colours-1: column_clicks_mod_colours;

% ================================================================ Constraints
% The row / column totals must match the clicks actually placed.
constraint forall(row in 1..board_size)(
  sum(column in 1..board_size)(clicks_per_square[row, column]) mod number_of_colours
    = row_clicks_mod_colours[row]
);
constraint forall(column in 1..board_size)(
  sum(row in 1..board_size)(clicks_per_square[row, column]) mod number_of_colours
    = column_clicks_mod_colours[column]
);

% Every square must end up with its goal colour:
%     row total + column total - clicks on the square = goal colour   (mod number_of_colours)
% Written as "clicks on the square = ...", so as soon as the solver picks a
% row total and a column total, the clicks on the square where they cross are
% known immediately.
% `+ number_of_colours` reason: MiniZinc's mod operator can return negative results.
constraint forall(row, column in 1..board_size)(
  clicks_per_square[row, column] =
    (row_clicks_mod_colours[row] + column_clicks_mod_colours[column]
     - goal_board[row, column] + number_of_colours) mod number_of_colours
);

% ================================================================ Symmetry breaking
% If two rows of the goal board are identical, swapping their totals gives a
% different solution that is just as good. Exploring both wastes time, so we
% only keep the one where the first row's total is not bigger than the
% second's. The same goes for identical columns. And if the goal board looks
% the same when flipped along its diagonal, swapping all row totals with all
% column totals is also just as good, so we keep only one of the two.
% We never remove the only best solution, only a copy of it.

% Helper tests on the goal board (plain true/false, no solver variables).
function bool: rows_are_identical(int: first_row, int: second_row) =
  forall(column in 1..board_size)(
    goal_board[first_row, column] = goal_board[second_row, column]);

function bool: columns_are_identical(int: first_column, int: second_column) =
  forall(row in 1..board_size)(
    goal_board[row, first_column] = goal_board[row, second_column]);

bool: goal_is_symmetric_on_diagonal =
  forall(row, column in 1..board_size)(
    goal_board[row, column] = goal_board[column, row]);

% Rule 1: identical rows -> the earlier row's total is not bigger.
constraint if use_symmetry_breaking then
  forall(first_row, second_row in 1..board_size
         where first_row < second_row /\ rows_are_identical(first_row, second_row))(
    row_clicks_mod_colours[first_row] <= row_clicks_mod_colours[second_row])
endif;

% Rule 2: identical columns -> the earlier column's total is not bigger.
constraint if use_symmetry_breaking then
  forall(first_column, second_column in 1..board_size
         where first_column < second_column /\ columns_are_identical(first_column, second_column))(
    column_clicks_mod_colours[first_column] <= column_clicks_mod_colours[second_column])
endif;

% Rule 3: goal looks the same flipped on its diagonal -> keep only one of
% "the solution" and "the solution flipped".
constraint if use_symmetry_breaking /\ goal_is_symmetric_on_diagonal then
  lex_lesseq(row_clicks_mod_colours, column_clicks_mod_colours)
endif;

% ================================================================ Objective
% Search over the row and column totals only; the clicks follow from them.
solve :: int_search(row_clicks_mod_colours ++ column_clicks_mod_colours,
                    input_order, indomain_min)
      minimize sum(clicks_per_square);

output [
  if column == 1 then "" else " " endif ++ show(clicks_per_square[row, column]) ++
  if column == board_size then "\n" else "" endif
  | row, column in 1..board_size
];
