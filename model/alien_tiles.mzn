% Symbolic Explainable Artificial Intelligence
% GROUP 18:
% Artur Krystopchuk (104145)
% Sofia Ligeiro (116046)
%
% Alien Tiles (CSPLib 027): minimum clicks per square that turn the all-zero
% board into goal_board

% ---------------------------------------------------------------- Instance
int: board_size;
int: number_of_colours;
array[1..board_size, 1..board_size] of 0..number_of_colours-1: goal_board;

% Symmetry breaking switch (on by default); only used by the benchmark
opt bool: break_symmetries;
bool: use_symmetry_breaking = break_symmetries default true;

% ---------------------------------------------------------------- Variables
array[1..board_size, 1..board_size] of var 0..number_of_colours-1: clicks_per_square;
array[1..board_size] of var 0..number_of_colours-1: row_clicks_mod_colours;
array[1..board_size] of var 0..number_of_colours-1: column_clicks_mod_colours;

% ---------------------------------------------------------------- Constraints
constraint forall(row in 1..board_size)(
  sum(column in 1..board_size)(clicks_per_square[row, column]) mod number_of_colours
    = row_clicks_mod_colours[row]
);
constraint forall(column in 1..board_size)(
  sum(row in 1..board_size)(clicks_per_square[row, column]) mod number_of_colours
    = column_clicks_mod_colours[column]
);

% clicks = row total + column total - goal (mod colours).
% "+ number_of_colours" because MiniZinc's mod can return negative values.
constraint forall(row, column in 1..board_size)(
  clicks_per_square[row, column] =
    (row_clicks_mod_colours[row] + column_clicks_mod_colours[column]
     - goal_board[row, column] + number_of_colours) mod number_of_colours
);

% ---------------------------------------------------------------- Symmetry breaking
function bool: rows_are_identical(int: first_row, int: second_row) =
  forall(column in 1..board_size)(
    goal_board[first_row, column] = goal_board[second_row, column]);

function bool: columns_are_identical(int: first_column, int: second_column) =
  forall(row in 1..board_size)(
    goal_board[row, first_column] = goal_board[row, second_column]);

bool: goal_is_symmetric_on_diagonal =
  forall(row, column in 1..board_size)(
    goal_board[row, column] = goal_board[column, row]);

% Identical rows: order their totals
constraint if use_symmetry_breaking then
  forall(first_row, second_row in 1..board_size
         where first_row < second_row /\ rows_are_identical(first_row, second_row))(
    row_clicks_mod_colours[first_row] <= row_clicks_mod_colours[second_row])
endif;

% Identical columns: order their totals.
constraint if use_symmetry_breaking then
  forall(first_column, second_column in 1..board_size
         where first_column < second_column /\ columns_are_identical(first_column, second_column))(
    column_clicks_mod_colours[first_column] <= column_clicks_mod_colours[second_column])
endif;

% Diagonal symmetry: keep only one of a solution and its transpose
constraint if use_symmetry_breaking /\ goal_is_symmetric_on_diagonal then
  lex_lesseq(row_clicks_mod_colours, column_clicks_mod_colours)
endif;

% ---------------------------------------------------------------- Objective
solve :: int_search(row_clicks_mod_colours ++ column_clicks_mod_colours,
                    input_order, indomain_min)
      minimize sum(clicks_per_square);

output [
  if column == 1 then "" else " " endif ++ show(clicks_per_square[row, column]) ++
  if column == board_size then "\n" else "" endif
  | row, column in 1..board_size
];
