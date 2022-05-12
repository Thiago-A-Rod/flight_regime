import numpy as np
import pandas as pd
from scipy.optimize import fsolve
from cvxopt import solvers
import cvxopt as cv


def quaternion_to_euler(df):
    '''
    this functions calculates the euler angles given the quaternions x,y,z,w
    :param df: [DataFrame] data frame with the quaternions named as x = df['x.1'], y = df['y.1'], z = df['z.1'] and w = df['w']
    :return: [series] euler angles phi, theta and psi in degrees
    '''
    t0 = +2.0 * (df['w'] * df['x.1'] + df['y.1'] *  df['z.1'])
    t1 = +1.0 - 2.0 * (df['x.1'] * df['x.1'] + df['y.1'] * df['y.1'])
    df['phi'] = np.arctan2(t0, t1)

    t2 = +2.0 * (df['w'] * df['y.1'] -  df['z.1'] * df['x.1'])
    t2[t2 > +1] = 1
    t2[t2 < -1] = -1
    df['theta'] = np.arcsin(t2)

    t3 = +2.0 * (df['w'] *  df['z.1'] + df['x.1'] * df['y.1'])
    t4 = +1.0 - 2.0 * (df['y.1'] * df['y.1'] +  df['z.1'] *  df['z.1'])
    df['psi'] = np.arctan2(t3, t4)

    return np.degrees(df['phi']), np.degrees(df['theta']), np.degrees(df['psi'])

def Thrust(m,gravity,phi,theta):
    '''
    this function calculates the Thrust based on the aircraft weight and euler angles
    :param m: [float] mass of the drone
    :param gravity: [float] gravity acceleration
    :param phi: [series] phi euler angle in degrees
    :param theta: [series] theta euler angles in degrees
    :return: [series] thrust values
    '''
    phi = np.radians(phi)
    theta = np.radians(theta)
    return m*gravity*np.sqrt((np.sin(phi)**2 *np.cos(theta)**2 + np.cos(phi)**2)/(np.cos(phi)**2 * np.cos(theta)**2))

def VairBody(df):
    '''
    this function returns the coordinates of the air velocity for the body frame, given the velocities from the vehicle
    frame and the euler angles;
    This method considers wind speed = 0.
    :param df:  [DataFrame] flight dataFrame
    :return: Vi^b, Vj^b, Vk^b
    '''

    psi = np.radians(df['psi'])
    phi = np.radians(df['phi'])
    theta = np.radians(df['theta'])
    Vair = np.asarray([df['x.2'],df['y.2'],df['z.2']]) #ground velocity
    Vair = Vair.reshape(Vair.shape[1], Vair.shape[0])
    #print(df.index.values)
    #print(Vair)
    ct = np.cos(theta)
    cph = np.cos(phi)
    cps = np.cos(psi)
    st = np.sin(theta)
    sph = np.sin(phi)
    sps = np.sin(psi)

    vx = df['x.2']*ct*cps + df['y.2']*ct*sps - df['z.2']*st
    vy = df['x.2']*(sph*st*cps-cph*sps) + df['y.2']*(sph*st*sps+cph*cps) + df['z.2']*(sph*ct)
    vz = df['x.2']*(cph*st*cps+sph*sps) + df['y.2']*(cph*st*sps-sph*sps) + df['z.2']*(cph*ct)

    vx = np.abs(vx)
    vy = np.abs(vy)
    vz = np.abs(vz)

    v = np.sqrt(vx**2 + vy**2 + vz**2)
    vai = np.sqrt(df['x.2']**2 + df['y.2']**2 + df['z.2']**2)

    R, vi, vj, vk = [],[],[],[] # todo: review why is not good...
    for row in list(df.index.values):
        ''' Rotation Matrix from Vehicle Frame to Body Frame '''
        R.append(np.asarray([[ct[row]*cps[row],ct[row]*sps[row],-st[row]],[sph[row]*st[row]*cps[row]-cph[row]*sps[
            row],sph[row]*st[row]*sps[row]+cph[row]*cps[row], sph[row]*ct[row]],[cph[row]*st[row]*cps[row]+sph[
            row]*sps[row],cph[row]*st[row]*sps[row]-sph[row]*sps[row],cph[row]*ct[row]]]))

    R = np.array(R)
    for row in range(len(R)):
        V = R[row].dot(Vair[row])
        vi.append(V[0])
        vj.append(V[1])
        vk.append(V[2])

    #return vi, vj, vk
    return vx, vy, vz

def InducedPower(df):
    '''
    this function returns the induced power in Watts
    :param df: [DataFrame] the flight data frame with Thrust = df['T']; alpha = df['alpha']; beta = df['beta'];
    Vbi =df['Vbi']; Vbj = df['Vbj']; Vbk = df['Vbj']
    :return: [series] induced power in Watts
    '''
    T = df['T']
    V_air = df['Vbi']**2 + df['Vbj']**2 + df['Vbj']**2
    V_air = np.sqrt(V_air.astype(float))
    v_i = df['v_i']
    alpha = np.radians(df['alpha'])
    beta = np.radians(df['beta'])
    P_i = T*(V_air*np.sqrt((np.sin(alpha)**2*np.sin(beta)**2-np.sin(alpha)**2)/(np.sin(alpha)**2*np.sin(beta)**2-1))+v_i)
    return P_i


def cvxopt_solve_qp(P, q, G=None, h=None, A=None, b=None):
    P = .5 * (P + P.T)  # make sure P is symmetric
    args = [cv.matrix(P), cv.matrix(q)]
    solvers.options['show_progress'] = True
    solvers.options['maxiters'] = 200
    if G is not None:
        args.extend([cv.matrix(G), cv.matrix(h)])
        if A is not None:
            args.extend([cv.matrix(A), cv.matrix(b)])
    sol = solvers.qp(*args)

    if 'optimal' not in sol['status']:
        return None
    return np.array(sol['x']).reshape((P.shape[1],))


def CalculateVreal(df):
    dfVread = df['wind_speed']
    psi = df['psi']
    theta = df['theta']
    phi = df['phi']
    WindAngle = df['wind_angle']

    dftheta = np.radians(theta)
    dfpsi = np.radians(psi)
    dfphi = np.radians(phi)
    dfWindAngle = np.radians(WindAngle)

    vreal_list = []
    vreal_i = []
    vreal_j = []
    vreal_k = []
    beta = []
    for i in df.index.values:
        Vread =dfVread[i]
        theta = dftheta[i]
        psi = dfpsi[i]
        phi = dfphi[i]
        WindAngle = dfWindAngle[i]

        P1 = 1
        P2 = np.sin(psi)/np.cos(psi)
        P3 = (np.sin(theta)/np.cos(theta))*np.sqrt(1+(np.sin(psi)/np.cos(psi))**2)
        P = np.asarray([P1,P2,P3]).reshape(1,3)
        Q = np.asarray([0,0,0]).reshape(1,3)
        S = np.asarray([0,1,np.sin(phi)/np.cos(phi)]).reshape(1,3)

        PQ = P - Q
        SQ = S - Q
        # Finding the normal vector to the plane
        NormalVector = np.cross(SQ, PQ)
        #print(NormalVector.shape)
        ModuleNormalVector = np.sqrt(NormalVector[:,0] ** 2 + NormalVector[:,1] ** 2 + NormalVector[:,2] ** 2)

        a1 = NormalVector[:,0] / ModuleNormalVector
        b1 = NormalVector[:,1] / ModuleNormalVector
        c1 = NormalVector[:,2] / ModuleNormalVector

        c2 = Vread * np.cos(WindAngle) / np.sqrt(1 + (c1 / a1) ** 2)

        a2 = -(c1 * c2 / a1)
        b2 = (Vread ** 2 - a2 ** 2 - c2 ** 2)
        b2 = np.where(b2 < 0, 0, b2)
        b2 = np.sqrt(b2)

        E = c2 / c1

        a3 = a1 * E
        b3 = b1 * E
        c3 = c2

        VReal = np.sqrt((a2 - a3) ** 2 + (b2 - b3) ** 2)

        VRealVector = np.asarray([a2 - a3, b2 - b3, c3 - c2])
        VRealVector = np.transpose(VRealVector)
        if WindAngle <= np.pi:
            beta.append(WindAngle - abs(psi))
        else:
            beta.append(2 * np.pi - WindAngle - abs(psi))

        #beta = np.degrees(np.where(WindAngle <= np.pi, abs(WindAngle) - abs(psi), 2 * np.pi - abs(WindAngle) - abs(
        # psi)))
        VRealVector[:,0] = np.abs(VRealVector[:,0])
        VRealVector[:,1] = np.abs(VRealVector[:,1])
        VRealVector[:,2] = np.abs(VRealVector[:,2])
        vreal_list.append(VReal)
        vreal_i.append(VRealVector[:,0])
        vreal_j.append(VRealVector[:,1])
        vreal_k.append(VRealVector[:,2])

    return vreal_list, vreal_i,vreal_j,vreal_k, beta











