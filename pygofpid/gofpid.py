
import numpy as np
import cv2 as cv


class GOFPID:
    """GOFPID: good old fashioned perimeter intrusion detection system.

    Using OpenCV, this class allows to build a pipeline using good old
    fashioned (GOF) computer vision methods for perimeter intrusion detection
    (PID):

    1. input frame denoising by spatial blurring;
    2. foreground detection by background subtraction;
    3. motion mask denoising by mathematical morphology;
    4. motion blob tracking (WIP);
    5. alarm.

    Parameters
    ----------
    blur : OpenCV bur filter | None, default={'fun': cv.GaussianBlur, \
            'ksize': (3, 3), 'borderType': cv.BORDER_DEFAULT}
        OpenCV filter for spatial blurring and its parameters:

        - cv.GaussianBlur for a Gaussian filter [GaussBlur]_;
        - cv.blur for a normalized box filter [BoxBlur]_;
        - None, no processing.

    frg_detect : OpenCV BackgroundSubtractor, default='MOG2'
        Method for foreground detection [BkgSub]_:

        - 'MOG2' for mixture of Gaussians [MOG2]_;
        - 'KNN' for K-nearest neigbours [KNN]_.

    mat_morph : list of dict | None, default=[ \
            {'fun': cv.erode, 'kernel': cv.getStructuringElement(cv.MORPH_RECT, (5, 5))}, \
            {'fun': cv.dilate, 'kernel': cv.getStructuringElement(cv.MORPH_RECT, (5, 5))}]
        List of dictionaries containing OpenCV operators for mathematical
        morphology, and their parameters: 'cv.erode' for erosion [Ersn]_, and
        'cv.dilate' for dilation [Dltn]_.
        If None, no processing.

    Attributes
    ----------
    motion_mask_ : ndarray of int, shape (n_height, n_width, n_color)
        Motion mask.

    References
    ----------
    .. [GaussBlur] https://docs.opencv.org/3.4.0/d4/d86/group__imgproc__filter.html#gaabe8c836e97159a9193fb0b11ac52cf1
    .. [BoxBlur] https://docs.opencv.org/3.4.0/d4/d86/group__imgproc__filter.html#ga8c45db9afe636703801b0b2e440fce37
    .. [BkgSub] https://docs.opencv.org/3.4.0/d7/df6/classcv_1_1BackgroundSubtractor.html
    .. [MOG2] https://docs.opencv.org/3.4.0/d7/d7b/classcv_1_1BackgroundSubtractorMOG2.html
    .. [KNN] https://docs.opencv.org/3.4.0/db/d88/classcv_1_1BackgroundSubtractorKNN.html
    .. [Ersn] https://docs.opencv.org/3.4.0/d4/d86/group__imgproc__filter.html#gaeb1e0c1033e3f6b891a25d0511362aeb
    .. [Dltn] https://docs.opencv.org/3.4.0/d4/d86/group__imgproc__filter.html#ga4ff0f3318642c4f469d0e11f242f3b6c
    """  # noqa
    def __init__(
        self,
        blur={
            'fun': cv.GaussianBlur,
            'ksize': (3, 3),
            'borderType': cv.BORDER_DEFAULT,
        },
        frg_detect='MOG2',
        mat_morph=[
            {
                'fun': cv.erode,
                'kernel': cv.getStructuringElement(cv.MORPH_RECT, (5, 5)),
            },
            {
                'fun': cv.dilate,
                'kernel': cv.getStructuringElement(cv.MORPH_RECT, (5, 5)),
            }
        ],
    ):
        self.blur = blur
        self.frg_detect = frg_detect
        self.mat_morph = mat_morph

    def fit(self):
        """Check parameters and set pipeline. No training.

        Returns
        -------
        self : object
            Returns self.
        """

        if self.blur:
            if 'fun' not in self.blur.keys():
                raise ValueError('Parameter blur has no key "fun".')
            if 'ksize' not in self.blur.keys():
                self.blur['ksize'] = (3, 3)
            if 'borderType' not in self.blur.keys():
                self.blur['borderType'] = cv.BORDER_DEFAULT

        if self.frg_detect == 'MOG2':
            self._frg_detect_mth = cv.createBackgroundSubtractorMOG2()
        elif self.frg_detect == 'KNN':
            self._frg_detect_mth = cv.createBackgroundSubtractorKNN()
        else:
            raise ValueError('Unknown method for background subtraction')

        if self.mat_morph:
            for d in self.mat_morph:
                if 'fun' not in d.keys():
                    raise ValueError('Parameter mat_morph has no key "fun".')
                if 'kernel' not in d.keys():
                    d['kernel'] = cv.getStructuringElement(
                        cv.MORPH_RECT,
                        (5, 5),
                    )

        return self

    def predict(self, X):
        """Predict if there is an intrusion in current frame.

        Parameters
        ----------
        X : ndarray of int, shape (n_height, n_width) or (n_height, n_width, n_channel)
            Input frame.

        Returns
        -------
        y : int
            Prediction of intrusion: 1 if intrusion detected, 0 otherwise.
        """
        # denoising by spatial blurring
        if self.blur:
            X = self.blur.get('fun')(
                X,
                self.blur.get('ksize'),
                self.blur.get('borderType'),
            )

        # foreground detection
        mask_ = self._frg_detect_mth.apply(X)

        # denoising by mathematical morphology
        if self.mat_morph:
            for d in self.mat_morph:
                mask_ = d.get('fun')(mask_, d.get('kernel'))

        self.motion_mask_ = mask_

        # motion blob tracking
        #self.motion_blob_

        # intrusion detection
        if np.any(self.motion_mask_):
            return 1
        else:
            return 0
