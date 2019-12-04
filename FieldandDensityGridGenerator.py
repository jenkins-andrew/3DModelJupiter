from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
import glob
from scipy.interpolate import griddata


def alfvenVelocityFuncForArray(magneticFieldArray, totalMassDensityArray):

    Va = magneticFieldArray * 1e-9 / np.sqrt(1.25663706212e-6 * totalMassDensityArray)

    return Va


def radialScaleHeight(r):
    """
    Finds the scale height at a radius
    :param r: Radius in R_J
    :return: Scale height in R_J
    """
    h = -0.116 + 2.14*np.log10(r/6) - 2.05*np.log10(r/6)**2 + 0.491*np.log10(r/6)**3 + 0.126*np.log10(r/6)**4
    H = 10 ** h
    return H


def radialVelocityFuncForArray(r, totalMassDensityArray):

    vr = 500/(2 * totalMassDensityArray * radialScaleHeight(r) * np.pi * r * 71492e3 ** 2)
    return vr


x, y, z, B, rho, alfvenPointCheck = [], [], [], [], [], []

for field_trace_path in glob.glob('output/postFieldLine/*.txt'):
    print(field_trace_path)
    x0, y0, z0, B0, rho0 = np.loadtxt(field_trace_path, delimiter='\t', unpack=True)
    x.extend(x0)
    y.extend(y0)
    z.extend(z0)
    B.extend(B0)
    rho.extend(rho0)

np.savetxt('temporaryFile.txt', np.c_[x, y, z, B, rho], delimiter='\t')
x, y, z, B, rho = np.loadtxt('temporaryFile.txt', delimiter='\t', unpack=True)

r = np.sqrt(x**2 + y**2 + z**2)
alfvenVelocity = alfvenVelocityFuncForArray(B, rho)
radialVelocity = radialVelocityFuncForArray(r, rho)

for i in range(len(alfvenVelocity)):
    if alfvenVelocity[i] > radialVelocity[i]:
        alfvenPointCheck.append(0)
    else:
        alfvenPointCheck.append(1)

np.savetxt('temporaryFile.txt', np.c_[x, r, z, B, rho, alfvenVelocity, radialVelocity, alfvenPointCheck], delimiter='\t')
x, r, z, B, rho, alfvenVelocity, radialVelocity, alfvenPointCheck = np.loadtxt('temporaryFile.txt', delimiter='\t', unpack=True)

maxR = 30
minR = 6
xtest = np.arange(-maxR, maxR+1, 0.5)
ztest = xtest
xtest, ztest = np.meshgrid(xtest, ztest)

# Masking a circle of radius minR R_J
mask = (xtest < minR) | (np.sqrt(xtest ** 2 + ztest ** 2) > maxR)

# Making the 3D grid for the magnetic field
BGrid = griddata((x, z), B, (xtest, ztest))
BGrid[mask] = np.nan

NGrid = griddata((x, z), rho, (xtest, ztest))
NGrid[mask] = np.nan

AlfvenGrid = griddata((x, z), alfvenVelocity/1000, (xtest, ztest))
AlfvenGrid[mask] = np.nan

RadialGrid = griddata((x, z), radialVelocity/1000, (xtest, ztest))
RadialGrid[mask] = np.nan

AlfvenPointGrid = griddata((x, z), alfvenPointCheck, (xtest, ztest))
AlfvenPointGrid[mask] = np.nan

plt.figure()
plt.plot(r, alfvenVelocity/1000, 'k', label='Alfven')
plt.plot(r, radialVelocity/1000, 'r', Label='Radial')
plt.yscale('log')
plt.ylim(1)
plt.ylabel('Velocity (km/s)', fontsize=18)
plt.xlabel('RJ', fontsize=18)
plt.legend(fontsize=18)
plt.xticks(size=18)
plt.yticks(size=18)
plt.tight_layout()

plt.figure()
heatmap = plt.contourf(xtest, ztest, BGrid, cmap=plt.cm.get_cmap('gist_rainbow'), alpha=0.4)
lines = plt.contour(xtest, ztest, BGrid, 5, colors='k')
plt.clabel(lines, fontsize=18, inline=1, colors='k')
clb = plt.colorbar(heatmap)
clb.ax.set_title('B$_n$ (nT)', fontsize=18)
plt.rcParams['xtick.labelsize'] = 18
plt.rcParams['ytick.labelsize'] = 18
plt.xlabel('x $(R_J)$', fontsize=18)
plt.ylabel('z $(R_J)$', fontsize=18)
plt.xticks(size=18)
plt.yticks(size=18)
plt.xlim(minR)
plt.tight_layout()

plt.figure()
heatmap = plt.contourf(xtest, ztest, NGrid, cmap=plt.cm.get_cmap('gist_rainbow'), alpha=0.4)
lines = plt.contour(xtest, ztest, NGrid, 5, colors='k')
plt.clabel(lines, fontsize=18, inline=1, colors='k')
clb = plt.colorbar(heatmap)
clb.ax.set_title(r'$\rho$ kgm$^{-3}$', fontsize=18)
plt.rcParams['xtick.labelsize'] = 18
plt.rcParams['ytick.labelsize'] = 18
plt.xlabel('x $(R_J)$', fontsize=18)
plt.ylabel('z $(R_J)$', fontsize=18)
plt.xlim(minR)
plt.xticks(size=18)
plt.yticks(size=18)
plt.tight_layout()

plt.figure()
plt.rcParams['xtick.labelsize'] = 18
plt.rcParams['ytick.labelsize'] = 18
plt.subplots_adjust(wspace=0.5, hspace=0.5)
plt.tight_layout()

ax = plt.subplot(221)
heatmap = plt.contourf(xtest, ztest, AlfvenGrid, cmap=plt.cm.get_cmap('gist_rainbow'), alpha=0.4)
lines = plt.contour(xtest, ztest, AlfvenGrid, 1, colors='k')
clb = plt.colorbar(heatmap)
clb.ax.set_title(r'(kms$^{-1}$)', fontsize=18)
plt.title('Alfven V', fontsize=18, wrap=True)
plt.xlabel('x $(R_J)$', fontsize=18)
plt.ylabel('y $(R_J)$', fontsize=18)
plt.xticks(size=18)
plt.yticks(size=18)
plt.xlim(minR)

ax = plt.subplot(222)
heatmap = plt.contourf(xtest, ztest, RadialGrid, cmap=plt.cm.get_cmap('gist_rainbow'), alpha=0.4)
lines = plt.contour(xtest, ztest, RadialGrid, 5, colors='k')
plt.clabel(lines, inline=1, colors='k')
clb = plt.colorbar(heatmap)
clb.ax.set_title(r'(kms$^{-1}$)', fontsize=18)
plt.title('Radial V', fontsize=18, wrap=True)
plt.xlabel('x $(R_J)$', fontsize=18)
plt.ylabel('y $(R_J)$', fontsize=18)
plt.xticks(size=18)
plt.yticks(size=18)
plt.xlim(minR)

ax = plt.subplot(212)
lines = plt.contour(xtest, ztest, AlfvenPointGrid, 1)
plt.title('Alfven Radius', fontsize=18, wrap=True)
plt.xlabel('x $(R_J)$', fontsize=18)
plt.ylabel('y $(R_J)$', fontsize=18)
plt.xticks(size=18)
plt.yticks(size=18)
plt.xlim(minR)

# ax = plt.subplot(224)
# alfvenmask = (alfvenVelocity > 0.95*radialVelocity) & (alfvenVelocity < 1.05*radialVelocity)
# calculatedRadius = np.sqrt(x ** 2 + y ** 2)
# phiwrong = np.arctan2(x, z)
# phi = np.mod(phiwrong, 2*np.pi) * 180 / np.pi
# # fit = np.poly1d(np.polyfit(phi[alfvenmask], calculatedRadius[alfvenmask], 3))
# plt.scatter(phi[alfvenmask], calculatedRadius[alfvenmask], s=0.1, color='k')
# # fitrange = np.arange(0, 360, 1)
# # plt.plot(fit(fitrange))
# plt.title('Alfven Radius', fontsize=18, wrap=True)
# plt.xlabel('Angle (Degrees)', fontsize=18)
# plt.ylabel('Radius (R$_J)$', fontsize=18)
# plt.xticks(size=18)
# plt.yticks(size=18)
# plt.xlim(minR)
plt.show()
