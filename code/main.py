import sys
from collections import deque

import matplotlib as mpl
import numpy as np
from PyQt5 import QtCore, QtWidgets

import Runge_Kutta as Rk
from ui import Ui

# Constants
rc0 = 0.6
m = 1
a = 4.3
t0 = 0
t = t0
dt = 0.025
tmaxn = 200
ti = 0

r0 = 1
Pr0 = 1

r = r0
Pr = Pr0

r_range = (-6, 6)
Pr_range = (-6, 6)
V_max = (-6, 6)

# Global Objects
r_rt = deque(maxlen=tmaxn)
Pr_rt = deque(maxlen=tmaxn)
t_rt = np.linspace(0, -tmaxn * dt, 200)

rS = np.linspace(*r_range, 1000)

stream = None
Vgraph1 = None
Vgraph2 = None

bgCache_rPr = None
bgCache_rV = None
bgCache_rt = None
bgCache_Prt = None

# Problem Funtions
V = lambda x: -a / x + a * rc0**2 / (3 * x**3)

rDotf = lambda Pr: Pr / m
PrDotf = lambda r: a * rc0**2 / r**4 - a / r**2


def PrepareFigure():
    global ax_rPr, ax_rV, ax_rt, ax_Prt

    axes = MyUI.canvas.fig.subplots(2, 2)

    ((ax_rPr, ax_rV), (ax_rt, ax_Prt)) = axes
    MyUI.canvas.fig.tight_layout(h_pad=2, w_pad=1)

    for axis in axes.reshape(4, 1):
        axis[0].cla()
        axis[0].yaxis.grid(color='gainsboro',
                           linestyle='dotted',
                           linewidth=1.5)
        axis[0].xaxis.grid(color='gainsboro',
                           linestyle='dotted',
                           linewidth=0.8)
        axis[0].axhline(0, linestyle='dotted', color='grey')
        axis[0].axvline(0, linestyle='dotted', color='grey')

    ax_rPr.set_title('Position vs Momentum')
    ax_rPr.set_xlabel(r'$r$', loc='right')
    ax_rPr.set_ylabel(r'$P_r$', loc='top', rotation=0)
    ax_rPr.set_xlim(r_range)
    ax_rPr.set_ylim(Pr_range)

    ax_rV.set_title('Position vs Potential')
    ax_rV.set_xlabel(r'$r$', loc='right')
    ax_rV.set_ylabel(r'$V(r)$', loc='top', rotation=0)
    ax_rV.set_xlim(r_range)
    ax_rV.set_ylim(V_max)

    ax_rt.set_title('Time vs Position')
    ax_rt.set_xlabel(r'$t$', loc='right')
    ax_rt.set_ylabel(r'$r(t)$', loc='top', rotation=0)
    ax_rt.set_xlim((-tmaxn * dt, tmaxn * dt / 5))
    ax_rt.set_ylim(r_range)

    ax_Prt.set_title('Time vs Momentum')
    ax_Prt.set_xlabel(r'$t$', loc='right')
    ax_Prt.set_ylabel(r'$Pr(t)$', loc='top', rotation=0)
    ax_Prt.set_xlim((-tmaxn * dt, tmaxn * dt / 5))
    ax_Prt.set_ylim(r_range)


def plot_fields():
    global stream, Vgraph1, Vgraph2
    density = 50

    # r vs Pr Plot
    if not (stream == None):
        stream.lines.remove()
        for art in ax_rPr.get_children():
            if not isinstance(art, mpl.patches.FancyArrowPatch):
                continue
            art.remove()

    rMesh, PrMesh = np.meshgrid(rS, np.linspace(*Pr_range, density))
    u = rDotf(PrMesh)
    v = PrDotf(rMesh)

    stream = ax_rPr.streamplot(rMesh,
                               PrMesh,
                               u,
                               v,
                               density=1.5,
                               arrowsize=0.7,
                               linewidth=0.5,
                               color='blue')

    # r vs V plot
    if not (Vgraph1 == None):
        Vgraph1.remove()
        Vgraph2.remove()
    Vgraph1, = ax_rV.plot(rS[:499], V(rS[:499]), color='blue', linewidth=0.7)
    Vgraph2, = ax_rV.plot(rS[500:], V(rS[500:]), color='blue', linewidth=0.7)

    MyUI.canvas.draw()


def plot_points(animated=False):
    global pointr, pointV, linert, linePrt

    pointr, = ax_rPr.plot(r,
                          Pr,
                          marker='o',
                          color='r',
                          markersize=4,
                          animated=animated)
    pointV, = ax_rV.plot(r,
                         V(r),
                         marker='o',
                         color='r',
                         markersize=4,
                         animated=animated)
    linert, = ax_rt.plot(t_rt[:len(r_rt)],
                         r_rt,
                         color='r',
                         marker='o',
                         markevery=[0],
                         markersize=4,
                         linewidth=0.8,
                         animated=animated)
    linePrt, = ax_Prt.plot(t_rt[:len(r_rt)],
                           Pr_rt,
                           color='g',
                           marker='o',
                           markevery=[0],
                           markersize=4,
                           linewidth=0.8,
                           animated=animated)


def animate():
    global t, r, Pr, r_rt, Pr_rt, ti

    t, r, Pr = next(rk4)

    r_rt.appendleft(r)
    Pr_rt.appendleft(Pr)

    update_points(blit=True)

    ti += 1


def start_animation():
    global ti

    solve_rk4()

    refresh_plots(animated=True)
    cache_bg()
    update_points(blit=True)

    ti = 0
    timer.start()


def cache_bg():
    global bgCache_rPr, bgCache_rV, bgCache_rt, bgCache_Prt

    bgCache_rPr = MyUI.canvas.copy_from_bbox(ax_rPr.bbox)
    bgCache_rV = MyUI.canvas.copy_from_bbox(ax_rV.bbox)
    bgCache_rt = MyUI.canvas.copy_from_bbox(ax_rt.bbox)
    bgCache_Prt = MyUI.canvas.copy_from_bbox(ax_Prt.bbox)


def stop_animation():
    timer.stop()
    refresh_plots()


def Redraw_fields():
    global m, a, rc0

    m = MyUI.txt_m.value()
    a = MyUI.txt_a.value()
    rc0 = MyUI.txt_rc0.value()

    plot_fields()
    refresh_plots()


def refresh_plots(animated=False):
    pointr.remove()
    pointV.remove()
    linert.remove()
    linePrt.remove()

    plot_points(animated=animated)

    MyUI.canvas.draw()


def update_points(blit=False):
    pointr.set_xdata(r)
    pointr.set_ydata(Pr)

    pointV.set_xdata(r)
    pointV.set_ydata(V(r))

    linert.set_xdata(t_rt[:len(r_rt)])
    linert.set_ydata(r_rt)

    linePrt.set_xdata(t_rt[:len(Pr_rt)])
    linePrt.set_ydata(Pr_rt)

    if blit == True:
        MyUI.canvas.restore_region(bgCache_rPr)
        ax_rPr.draw_artist(pointr)
        MyUI.canvas.blit(ax_rPr.bbox)

        MyUI.canvas.restore_region(bgCache_rV)
        ax_rV.draw_artist(pointV)
        MyUI.canvas.blit(ax_rV.bbox)

        MyUI.canvas.restore_region(bgCache_rt)
        ax_rt.draw_artist(linert)
        MyUI.canvas.blit(ax_rt.bbox)

        MyUI.canvas.restore_region(bgCache_Prt)
        ax_Prt.draw_artist(linePrt)
        MyUI.canvas.blit(ax_Prt.bbox)

        MyUI.canvas.flush_events()
    elif blit == False:
        MyUI.canvas.draw()


def on_click(event: mpl.backend_bases.MouseEvent):
    global r_rt, Pr_rt, r, Pr

    stop_animation()

    if event.inaxes in [ax_rPr]:
        r_rt = deque(maxlen=tmaxn)
        Pr_rt = deque(maxlen=tmaxn)

        r = event.xdata
        Pr = event.ydata

        update_points()

    if event.inaxes in [ax_rV]:
        r_rt = deque(maxlen=tmaxn)
        Pr_rt = deque(maxlen=tmaxn)
        r = event.xdata

        update_points()


def solve_rk4():
    global rk4

    def f(t, r, Pr):
        return rDotf(Pr)

    def g(t, r, Pr):
        return PrDotf(r)

    rk4 = Rk.RKG_Generator(F=[f, g],
                           xi=0,
                           yi=[r, Pr],
                           h=dt,
                           Bt=Rk.Butcher_Tableau('Classic-4th'))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    MyUI = Ui()
    MyUI.Button_Run.clicked.connect(start_animation)
    MyUI.Button_Pause.clicked.connect(stop_animation)
    MyUI.Button_Redraw.clicked.connect(Redraw_fields)
    MyUI.canvas.mpl_connect("button_press_event", on_click)

    MyUI.txt_rc0.setValue(rc0)
    MyUI.txt_m.setValue(m)
    MyUI.txt_a.setValue(a)

    PrepareFigure()
    plot_fields()
    plot_points()

    timer = QtCore.QTimer()
    timer.setInterval(50)
    timer.timeout.connect(animate)

    MyUI.showMaximized()
    app.exec_()