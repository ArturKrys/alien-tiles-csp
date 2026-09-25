% Symbolic Explainable Artificial Intelligence
% GROUP 18: 
% Artur Krystopchuk (104145)
% Sofia Ligeiro (116046)

int: n;                                  % board size (n x n)
int: c;                                  % number of colours
array[1..n,1..n] of int: goal;           % goal board
array[1..n,1..n] of var 0..c-1: clicks;  % number of times a square is clicked

% (all clicks in row r) + (all clicks in column s) - clicks[r,s]
constraint forall(r in 1..n, s in 1..n)(
  (sum(j in 1..n)(clicks[r,j]) + sum(i in 1..n)(clicks[i,s]) - clicks[r,s])
    mod c == goal[r,s]
);

% Among all valid click patterns, prefer the one with fewest total clicks.
solve minimize sum(i,j in 1..n)(clicks[i,j]);

output [
  if j == 1 then "" else " " endif ++ show(clicks[i,j]) ++
  if j == n then "\n" else "" endif
  | i in 1..n, j in 1..n
];
