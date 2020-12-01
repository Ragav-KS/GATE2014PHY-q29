import numpy as np

def RKG_Generator(F: list, xi: float, yi: list, h: float, Bt):

    yn = yi
    xn = xi
    var = len(yn)
    hk = np.zeros((var, Bt['s']))
    while True:

        hk.fill(0)

        # k_i
        for i in range(Bt['s']):
            xt = xn
            yt = yn.copy()

            yt += hk.dot(Bt['A'][i])
            for m in range(var):
                hk[m, i] = h * F[m](xt, *yt)
        # y_{n+1}
        for i in range(var):
            yn[i] += np.array(Bt['B']).dot(hk[i])
        xn = xt + Bt['C'][i] * h
        yield (xn, *yn)

#yapf: disable
def Butcher_Tableau(method=None):
    if method == None:
        Meth_list = ['Forward Euler',
                     'Explicit Midpoint',
                     'Ralston',
                     'Kutta-3rd',
                     'Classic-4th']
        return Meth_list
    elif method == 'Forward Euler':
        C =  [  0   ]
        A = [[  0   ]]
        B =  [  1   ]
    elif method == 'Explicit Midpoint':
        C =  [  0,      1/2 ]
        A = [[  0,      0   ],
             [  1/2,    0   ]]
        B =  [  0 ,     1   ]
    elif method == 'Ralston':
        C =  [  0,      2/3 ]
        A = [[  0,      0   ],
             [  2/3,    0   ]]
        B =  [  1/4,    3/4 ]
    elif method == 'Kutta-3rd':
        C =  [  0,      1/2,    1   ]
        A = [[  0,      0,      0   ],
             [  1/2,    0,      0   ],
             [  -1,     2,      0   ]]
        B =  [  1/6,    2/3,    1/6 ]
    elif method == 'Classic-4th':
        C =  [  0,      1/2,    1/2,    1   ]
        A = [[  0,      0,      0,      0   ],
             [  1/2,    0,      0,      0   ],
             [  0,      1/2,    0,      0   ],
             [  0,      0,      1,      0   ]]
        B =  [  1/6,    1/3,    1/3,    1/6 ]

    return {'s':    len(C),
            'C':    np.array(C),
            'A':    np.array(A),
            'B':    np.array(B)}
#yapf: enable