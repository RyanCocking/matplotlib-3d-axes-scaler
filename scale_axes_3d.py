# Adjust the lengths of the axes in a Matplotlib 3D plot
from mpl_toolkits.mplot3d.axes3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def scale_3d_projection(scale_x=1, scale_y=1, scale_z=1):
    """Wrapper with input args for get_proj_scaled()"""

    # axes are scaled down to fit in scene
    max_scale = max(scale_x, scale_y, scale_z)

    scale_x = scale_x / max_scale
    scale_y = scale_y / max_scale
    scale_z = scale_z / max_scale

    scale = np.array(
        [[scale_x, 0, 0, 0],
         [0, scale_y, 0, 0],
         [0, 0, scale_z, 0],
         [0, 0, 0, 1]]
    )

    def get_proj_scaled(self):
        """
        Create the projection matrix from the current viewing position

        Alternative implementation of 'mpl_toolkits.mplot3d.axes3d.get_proj()'

        Original solution: https://stackoverflow.com/questions/30223161/how-to-increase-the-size-of-an-axis-stretch-in-a-3d-plot
        """

        # elev: elevation angle in the z plane
        # azim: azimuth angle in the x,y plane
        relev, razim = np.pi * self.elev / 180, np.pi * self.azim / 180

        xmin, xmax = self.get_xlim3d()
        ymin, ymax = self.get_ylim3d()
        zmin, zmax = self.get_zlim3d()

        # transform to uniform world coordinates 0-1, 0-1, 0-1
        worldM = proj3d.world_transformation(xmin, xmax, ymin, ymax, zmin, zmax)

        # look into the middle of the new coordinates
        R = np.array([0.5, 0.5, 0.5])

        # dist: distance of the eye viewing point from the object point
        xp = R[0] + np.cos(razim) * np.cos(relev) * self.dist
        yp = R[1] + np.sin(razim) * np.cos(relev) * self.dist
        zp = R[2] + np.sin(relev) * self.dist
        E = np.array((xp, yp, zp))

        # eye: coordinates for the eye viewing point
        self.eye = E
        self.vvec = R - E
        self.vvec /= np.linalg.norm(self.vvec)

        if abs(relev) > np.pi / 2:
            # upside down
            V = np.array((0, 0, -1))
        else:
            V = np.array((0, 0, 1))

        zfront = -self.dist
        zback = self.dist

        viewM = proj3d.view_transformation(E, R, V, roll=0)
        perspM = proj3d.persp_transformation(zfront, zback, focal_length=1.2)
        M0 = np.dot(viewM, worldM)
        M = np.dot(perspM, M0)

        return np.dot(M, scale)

    return get_proj_scaled


if __name__ == "__main__":

    # Customisable parameters: https://matplotlib.org/stable/users/explain/customizing.html
    mpl.rcParams["axes.labelsize"] = 16
    mpl.rcParams["axes.labelpad"] = 12

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
    z = np.linspace(-2, 2, 100)
    r = z**2 + 1
    x = r * np.sin(theta)
    y = r * np.cos(theta)

    ax.plot(x, y, z, label="parametric curve")

    ax.set_xlabel("x", weight="bold")
    ax.set_ylabel("y", weight="bold")
    ax.set_zlabel("z", weight="bold")

    Axes3D.get_proj = scale_3d_projection(1, 2, 3)

    plt.show()