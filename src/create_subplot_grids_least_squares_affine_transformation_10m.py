from matplotlib import pyplot as plt
import numpy as np
from math import pi

box_labels = {}
box_labels["maliau_belian"] = ["01", "02", "03", "04", "05", "10", "09", "08", "07", "06", "11", "12", "13", "14", "15", "20", "19", "18", "17", "16", "21", "22", "23", "24", "25"]
box_labels["B_north"] = ["01", "02", "03", "04", "05", "10", "09", "08", "07", "06", "11", "12", "13", "14", "15", "20", "19", "18", "17", "16", "21", "22", "23", "24", "25"]
box_labels["B_south"] = ["01", "02", "03", "04", "05", "10", "09", "08", "07", "06", "11", "12", "13", "14", "15", "20", "19", "18", "17", "16", "21", "22", "23", "24", "25"]
box_labels["LFE"] = ["01", "02", "03", "04", "05", "10", "09", "08", "07", "06", "11", "12", "13", "14", "15", "20", "19", "18", "17", "16", "21", "22", "23", "24", "25"]
box_labels["maliau_seraya"] = ["01", "02", "03", "04", "05", "06", "11", "10", "09", "08", "07", "_", "12", "13", "14", "15", "16", "_", "21", "20", "19", "18", "17", "_", "22", "23", "24", "25","_","_"]
box_labels["E"] = ["01","02","03","04","05","06","07","14","13","12","11","10","09","08","_","_","15","16","17","18","19","_","_","22","21","20","_","_","_","_","23","24","25","_","_"]
# Danum plots orientated so that top is positioned to the north!
box_labels["danum_1"] = ["21", "20", "11", "10", "01", "22", "19", "12", "09", "02", "23", "18", "13", "08", "03", "24", "17", "14", "07", "04", "25", "16", "15", "06", "05"]
box_labels["danum_2"] = ["21", "20", "11", "10", "01", "22", "19", "12", "09", "02", "23", "18", "13", "08", "03", "24", "17", "14", "07", "04", "25", "16", "15", "06", "05"]

#C_plots
outfile = "BALI_subplot_coordinates_corrected_10m_grid.csv"
#plot = ["maliau_belian", "maliau_seraya", "B_north", "B_south", "LFE", 'E', 'danum_1', 'danum_2']

# load in GPS points and regular gridpoints from file
gps_pts_file = 'GPS_points_file_for_least_squares_fitting.csv'
datatype = {'names': ('plot', 'x', 'y', 'x_prime', 'y_prime'), 'formats': ('U16','f16','f16','f16','f16')}
plot_coordinates = np.genfromtxt(gps_pts_file, skip_header=True, delimiter = ',',dtype=datatype)


# loop through plots
plots = np.unique(plot_coordinates['plot'])
n_plots = plots.size
subplot_bbox = []
subplot_bbox_alt = []
subplot_labels=[]
bbox10m_x=[]
bbox10m_y=[]
labels10m=[]
for pp in range(0, n_plots):
    # first get points for a given plot and build matrices
    mask = plot_coordinates['plot']==plots[pp]
    n_points_in_polygon = plot_coordinates['x'][mask].size
    A=np.zeros((2*n_points_in_polygon,6))
    b=np.zeros(2*n_points_in_polygon)

    for ii in range(0,n_points_in_polygon):
        A[ii,0]=plot_coordinates['x'][mask][ii]
        A[ii,1]=plot_coordinates['y'][mask][ii]
        A[ii,2]=1

        A[ii+n_points_in_polygon,3]=plot_coordinates['x'][mask][ii]
        A[ii+n_points_in_polygon,4]=plot_coordinates['y'][mask][ii]
        A[ii+n_points_in_polygon,5]=1

        b[ii] = plot_coordinates['x_prime'][mask][ii]
        b[ii+n_points_in_polygon] = plot_coordinates['y_prime'][mask][ii]

    # now perform least squares inversion to find parameters of the optimal 2D rotation-translation affine transformation
    h, res, rank, s = np.linalg.lstsq(A,b)

    # now construct the affine transformation matrix
    affine = np.zeros((3,3))
    affine[0,0]=h[0]
    affine[0,1]=h[1]
    affine[0,2]=h[2]
    affine[1,0]=h[3]
    affine[1,1]=h[4]
    affine[1,2]=h[5]
    affine[2,0]=0
    affine[2,1]=0
    affine[2,2]=1

    # now we have affine transformation, set up the subplot grids
    plot_width = 100.
    subplot_width = 20

    rows = 5
    cols = 5
    if plots[pp]=="maliau_seraya":
        cols = 6
    if plots[pp]=='E':
        cols = 7

    x=np.arange(0,cols+1.)*subplot_width
    y=np.arange(0,rows+1.)*subplot_width

    xv,yv=np.asarray(np.meshgrid(x,y))

    xv=xv.reshape(xv.size)
    yv=yv.reshape(yv.size)

    xy=np.asarray([xv,yv])

    n_points_in_grid = xv.size
    xi=np.zeros(n_points_in_grid)
    yi=np.zeros(n_points_in_grid)
    for ii in range(0,n_points_in_grid):
        Xi = np.ones((3,1))
        Xi[0]=xv[ii]
        Xi[1]=yv[ii]

        Xi_prime = np.dot(affine,Xi)
        xi[ii] = Xi_prime[0]
        yi[ii] = Xi_prime[1]

    x_prime = xi.reshape(rows+1,cols+1)
    y_prime = yi.reshape(rows+1,cols+1)

    count = 0
    subplot=[]
    #fig,ax = plt.subplots(nrows=1,ncols=1, facecolor='White',figsize=[6,6])
    #ax1 = plt.subplot2grid((1,1),(0,0))
    #ax1.set_aspect('equal')
    #ax1.set_title(plots[pp])
    for i in range(0,rows):
        for j in range(0,cols):
            bbox = [ [x_prime[i,j], x_prime[i+1,j], x_prime[i+1,j+1], x_prime[i,j+1], x_prime[i,j]],
                     [y_prime[i,j], y_prime[i+1,j], y_prime[i+1,j+1], y_prime[i,j+1], y_prime[i,j]] ]
            if box_labels[plots[pp]][count]!="_":
                subplot_bbox.append(bbox)
            bbox_alt = [ x_prime[i,j], y_prime[i,j], x_prime[i+1,j], y_prime[i+1,j], x_prime[i+1,j+1],
                         y_prime[i+1,j+1], x_prime[i,j+1], y_prime[i,j+1], x_prime[i,j], y_prime[i,j] ]
            if box_labels[plots[pp]][count]!="_":
                subplot_bbox_alt.append(bbox_alt)
                subplot.append(box_labels[plots[pp]][count])
            count+=1
    bboxes = np.asarray(subplot_bbox)
    #for i in range(0,25):
    #    ax1.plot(bboxes[25*pp+i,0,:],bboxes[25*pp+i,1,:],'-',color='red')

    # Now need to label the bounding boxes and ignore those that aren't required
    N_sub = len(subplot)
    tag = ['aa','ab','ac','ad','ba','bb','bc','bd','ca','cb','cc','cd','da','db','dc','dd']
    for i in range(0,N_sub):
        subplot_labels.append((str(plots[pp])+", "+str(subplot[i])))
        for t in tag:
            labels10m.append(str(plots[pp])+", "+str(subplot[i])+t)


    # Alternative, regrid subplots to a finer resolution
    count = 0
    new_res = 5
    scale = new_res/subplot_width
    for i in range(0,rows):
        for j in range(0,cols):
            if box_labels[plots[pp]][count]!="_":
                x00 = x_prime[i,j]; x01 = x_prime[i,j+1]; x10 = x_prime[i+1,j]
                y00 = y_prime[i,j]; y01 = y_prime[i,j+1]; y10 = y_prime[i+1,j]
                for ii in range(0,int(1/scale)):
                    for jj in range(0,int(1/scale)):
                        bbox_x = [ x00+scale*(jj*(x01-x00)+ii*(x10-x00)),
                                        x00+scale*(jj*(x01-x00)+(ii+1)*(x10-x00)),
                                        x00+scale*((jj+1)*(x01-x00)+(ii+1)*(x10-x00)),
                                        x00+scale*((jj+1)*(x01-x00)+(ii)*(x10-x00)),
                                        x00+scale*(jj*(x01-x00)+ii*(x10-x00)) ]
                        bbox_y = [ y00+scale*(jj*(y01-y00)+ii*(y10-y00)),
                                        y00+scale*(jj*(y01-y00)+(ii+1)*(y10-y00)),
                                        y00+scale*((jj+1)*(y01-y00)+(ii+1)*(y10-y00)),
                                        y00+scale*((jj+1)*(y01-y00)+(ii)*(y10-y00)),
                                        y00+scale*(jj*(y01-y00)+ii*(y10-y00)) ]
                        bbox10m_x.append(bbox_x)
                        bbox10m_y.append(bbox_y)
                        #ax1.plot(bbox_x,bbox_y,'-.',color='blue')
            count+=1
    #fig.show()
"""
f = open(outfile,"w") #opens file
f.write("Plot, Subplot, x11, y11, x12, y12, x22, y22, x21, y21, x11, y11\n")

for i in range(0,len(subplot_labels)):
    f.write(subplot_labels[i]+", ")
    for j in range(0,9):
        f.write(str(subplot_bbox_alt[i][j]))
        f.write(", ")

    f.write(str(subplot_bbox_alt[i][9]))
    f.write("\n")
f.close()
"""
f = open(outfile,"w") #opens file
f.write("Plot, Subplot, x11, y11, x12, y12, x22, y22, x21, y21, x11, y11\n")

for i in range(0,len(labels10m)):
    f.write(labels10m[i]+", ")
    for j in range(0,4):
        f.write(str(bbox10m_x[i][j]))
        f.write(", ")
        f.write(str(bbox10m_y[i][j]))
        f.write(", ")
    f.write(str(bbox10m_x[i][4]))
    f.write(str(bbox10m_y[i][4]))
    f.write("\n")
f.close()