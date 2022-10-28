# Project1-Sudoku
Luyang Wang

This project information can be found in [Colab](https://colab.research.google.com/drive/1RNR3bkramHc2iVacBwHDR13IW78k7fWs)

In this project, I consider the constrained optimization problem for Sudoku with the following integer constraints. 
Let x_{ijk} indicate the event that the (i, j) element of the Sudoku grid contains k. If it is true, x_{ijk}=1, otherwise x_{ijk} = 0.  Then the constraints are 

- Column, sum_{i=1}^9 x_{ijk} = 1 for 1 <= j,k <= 9
- Row, sum_{j=1}^9 x_{ijk} = 1 for 1 <= i,k <= 9
- Box, sum_{j=3p-2}^{3p} \sum_{i= 3q-2}^{3q} x_{ijk} = 1 for 1 <= k <= 9 and 1 <= p,q <= 3. 
-  Grid, sum_{k=1}^{9} x_{ijk} = 1 for 1 <= i,j <= 9. 
- Clues, should be given from the problem.

The integer constraint is x_{ijk} in {0, 1}. 

Since integer optimization is usually Np-hard, I can relax the problem a little bit to allow floating point variables instead of integers. The problem can be replaced by minf(X), subject to the linear constraints AX=B for some chosen f. 

In this case, we can demonstrate the LP for the Sudoku problem. min_{X}||X||_L, subject to equality constraint AX = B. 

The code of Soduku solver is inspired by the reference. 

Reference:
https://www.kaggle.com/gaz3ll3/simple-lp-solver-for-sudoku-success-rate-0-32
