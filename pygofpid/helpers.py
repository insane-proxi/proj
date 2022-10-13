"""Helpers."""

import numpy as np
import cv2 as cv


def get_first_frame(video_filename):
    """Get first frame of video."""
    vidcap = cv.VideoCapture(video_filename)
    if not vidcap.isOpened():
        raise ValueError('Unable to open input filemane.')
    _, frame = vidcap.read()
    vidcap.release()
    return frame


def display_window(window_name, img, clone):
    """Dispay window."""
    while True:
        cv.imshow(window_name, img)
        key = cv.waitKey(1) & 0xFF
        if key == ord("r"):  # 'r' key => reset window
            img = clone.copy()
        elif key == ord("c"):  # 'c' key => close
            cv.destroyWindow(window_name)
            break


def plot_rectangles(X, rects, thickness):
    cv.rectangle(X, rects[0], rects[1], (0, 0, 255), 2)
    cv.rectangle(X, rects[0] - thickness, rects[0] + thickness, (0, 0, 255), -1)
    cv.rectangle(X, rects[1] - thickness, rects[1] + thickness, (0, 0, 255), -1)
    cv.rectangle(X, rects[2], rects[3], (0, 0, 255), 2)
    cv.rectangle(X, rects[2] - thickness, rects[2] + thickness, (0, 0, 255), -1)
    cv.rectangle(X, rects[3] - thickness, rects[3] + thickness, (0, 0, 255), -1)


def get_centers(contours, dtype=np.int16):
    """Compute centers of contours."""
    centers = []
    for contour in contours:
        moments = cv.moments(contour)
        x = int(moments["m10"] / moments["m00"])
        y = int(moments["m01"] / moments["m00"])
        centers.append([x, y])
    return np.array(centers, dtype=dtype)


def get_bottoms(contours, dtype=np.int16):
    """Compute middle-bottom points of contours."""
    bottoms = []
    for contour in contours:
        moments = cv.moments(contour)
        x = int(moments["m10"] / moments["m00"])
        y = max(contour[..., 1])  # downward axis => bottom = max
        bottoms.append([x, y])
    return np.array(bottoms, dtype=dtype)

def is_in_rectangles(coord, centers, thickness):
    for i, center in enumerate(centers):
        if cv.pointPolygonTest(
            np.array([
                [center[0] - thickness[0], center[1] - thickness[1]],
                [center[0] - thickness[0], center[1] + thickness[1]],
                [center[0] + thickness[0], center[1] + thickness[1]],
                [center[0] + thickness[0], center[1] - thickness[1]],
            ]),
            coord,
            False,
        ) >= 0:
            return i
    else:
        return -1


def normalize_coords(coords, shape):
    """Transform image coords (x,y) into normalized coords in [0,1]."""
    ncoords = np.asarray(coords, dtype=np.float64)
    ncoords[..., 0] /= shape[1]
    ncoords[..., 1] /= shape[0]
    return ncoords


def unnormalize_coords(ncoords, shape, dtype=np.uint8):
    """Transform normalized coords (x,y) in [0,1] into image coords."""
    coords = np.asarray(ncoords, dtype=np.float64)
    coords[..., 0] *= shape[1]
    coords[..., 1] *= shape[0]
    return coords.astype(dtype)


class SimpleLinearRegression():
    """Simple linear regression."""
    def __init__(self):
        self.coeff = None
        self.intercept = None

    def fit(self, x, y):
        """Fit linear model.

        Fit the parameters (a,b) of a simple linear regression between two
        samples, such as: y = a * x + b

        Parameters
        ----------
        x : ndarray, shape (2,)
            Training values.
        y : ndarray, shape (2,)
            Target values.
        """
        self.coeff = (y[1] - y[0]) / (x[1] - x[0])
        self.intercept = y[0] - self.coeff * x[0]
        return self

    def predict(self, x):
        """Predict using the linear model.

        Predict value y from input x using a simple linear regression:
        y = a * x + b.

        Parameters
        ----------
        x : ndarray, shape (n,)
            Input values.

        Returns
        -------
        y : ndarray, shape (n,)
            Predicted values.
        """
        return self.coeff * x + self.intercept
