# -*- coding: utf-8 -*-
"""soduku.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fV9yMjuCkANOiP9hmSfF8Ek_y6hCutMq
"""

from google.colab import drive
drive.mount('/content/drive')
import sys
sys.path.insert(0,'/content/drive/My Drive/110bprojects')

import numpy as np
import matplotlib.pyplot as plt 
import pandas as pd
np.random.seed(42)

#Read files
small1 = pd.read_csv("/content/drive/My Drive/110bprojects/small1.csv")
small2 = pd.read_csv("/content/drive/My Drive/110bprojects/small2.csv")
large1 = pd.read_csv("/content/drive/My Drive/110bprojects/large1.csv")
large2 = pd.read_csv("/content/drive/My Drive/110bprojects/large2.csv")

import scipy.sparse as scs 
import scipy.linalg as scl 
import scipy.optimize as sco

"""Reference: https://www.kaggle.com/gaz3ll3/sudoku-challenge-example-1"""

def integer_constraints(N=9):
    #For each row, sum of x_(ijk) from j = 1 to 9 is 1, while 1<=i,k<=9. 
    rowC = np.zeros(N) 
    rowC[0] =1
    row = np.zeros((N,N))   
    for i in range(N):
        row[i,i] = 1 #Generate a 9*9 matrix with the diagonal = 1.
    ROW = np.kron(row, np.kron(np.ones((1,N)), np.eye(N))) #Generate Kronecker product 

    #For each column, sum of x_(ijk) from i = 1 to 9 is 1, while 1<=j,k<=9. 
    colR = np.kron(np.ones((1,N)), rowC)
    col  = scl.toeplitz(rowC, colR)
    COL  = np.kron(col, row) #Generate a 243*243 matrix with the diagonal = 1.
    
    #For each box, sum of x_(ijk) from i = 3q-2 to 3q and j = 3p-2 to 3p is 1, while 1<=k<=9 and 1<=p,q<=3. 
    M = int(np.sqrt(N))
    boxC = np.zeros(M)
    boxC[0]=1
    boxR = np.kron(np.ones((1, M)), boxC) 
    box = scl.toeplitz(boxC, boxR)
    box = np.kron(np.eye(M), box)
    BOX = np.kron(box, np.block([np.eye(N), np.eye(N), np.eye(N)])) #Generate a 243*243 matrix with the diagonal = 1.
    
    #For each grid, sum of x_(ijk) from k = 1 to 9 is 1, while 1<=i,j<=9.
    grid = np.eye(N**2)
    GRID = np.kron(grid, np.ones((1,N)))
    
    return scs.csr_matrix(np.block([[ROW],[COL],[BOX],[GRID]]))

def clue_constraint(input_quiz, N=9):
    #Extract the nonzeros from the quiz string. Get the constraint matrix from clue. 
    m = np.reshape([int(c) for c in input_quiz], (N,N))
    r, c = np.where(m.T)
    v = np.array([m[c[d],r[d]] for d in range(len(r))])
    
    table = N * c + r
    table = np.block([[table],[v-1]])
    
    # it is faster to use lil_matrix when changing the sparse structure.
    CLUE = scs.lil_matrix((len(table.T), N**3))
    for i in range(len(table.T)):
        CLUE[i,table[0,i]*N + table[1,i]] = 1
    # change back to csr_matrix.
    CLUE = CLUE.tocsr() 
    
    return CLUE

import time

corr_cnt = 0
start = time.time()

#generate 1000 samples if the length is greater than 1000. 
if len(large1) > 1000:
    samples = np.random.choice(len(large1), 1000)
else:
    samples = range(len(large1))

for i in range(len(samples)):
    quiz = large1["quizzes"][samples[i]]
    solu = large1["solutions"][samples[i]]
    #Formulate both the integer constraints and clue constraints. 
    A0 = integer_constraints()
    A1 = clue_constraint(quiz)

    # Formulate the matrix A and vector B (B is all ones).
    A = scs.vstack((A0,A1))
    A = A.toarray()
    B = np.ones(A.shape[0])


    # Because rank defficiency. We need to extract effective rank.
    u, s, vh = np.linalg.svd(A, full_matrices=False)
    K = np.sum(s > 1e-12)
    S = np.block([np.diag(s[:K]), np.zeros((K, A.shape[0]-K))])
    A = S@vh
    B = u.T@B
    B = B[:K]

    c = np.block([ np.ones(A.shape[1]), np.ones(A.shape[1]) ])
    G = np.block([[-np.eye(A.shape[1]), np.zeros((A.shape[1], A.shape[1]))],\
                         [np.zeros((A.shape[1], A.shape[1])), -np.eye(A.shape[1])]])
    h = np.zeros(A.shape[1]*2)
    H = np.block([A, -A])
    b = B

    ret = sco.linprog(c, G, h, H, b, method='interior-point', options={'tol':1e-6})
    x = ret.x[:A.shape[1]] - ret.x[A.shape[1]:]

    
    z = np.reshape(x, (81, 9))
    if np.linalg.norm(np.reshape(np.array([np.argmax(d)+1 for d in z]), (9,9) ) \
                      - np.reshape([int(c) for c in solu], (9,9)), np.inf) >0:
        pass
    else:
        #print("CORRECT")
        corr_cnt += 1

    if (i+1) % 20 == 0:
        end = time.time()
        print("Aver Time: {t:6.2f} secs. Success rate: {corr} / {all} ".format(t=(end-start)/(i+1), corr=corr_cnt, all=i+1) )

end = time.time()
print("Aver Time: {t:6.2f} secs. Success rate: {corr} / {all} ".format(t=(end-start)/(i+1), corr=corr_cnt, all=i+1) )