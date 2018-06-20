#!/usr/bin/env python
"""Find shapes in a card image."""

import os
import sys
import cv2
import numpy as np
from common import (
  SHAPES_OUT_DIR,
  display_im,
  write_im,
  clean_make_dir,
  rectify,
  expand_points
)

# min channel cutoff for the threshold filter
THRESH_MIN = 180

OUT_WIDTH = 100
OUT_HEIGHT = 200

def find_shapes(card_file, 
                out_w=OUT_WIDTH,
                out_h=OUT_HEIGHT,
                display_shapes=False):
  """Given a card image file, cut out and return the 1, 2, or 3 shapes
  on the card. Returns a list of lists of 4 points, corner coordinates of
  each bounding box.
  """
  # a lot of this function is the same as card_finder.py's find_cards,
  # TODO refactor for both to inherit from a common function
  orig_im = cv2.imread(card_file, 1)
  im = cv2.imread(card_file, 0)
  blur = cv2.GaussianBlur(im,(1,1),1000)
  flag, thresh = cv2.threshold(blur, THRESH_MIN, 255, cv2.THRESH_BINARY)

  # invert, otherwise RETR_EXTERNAL makes the whole card the largest contour
  thresh = cv2.bitwise_not(thresh)

  # `image` is the thrown away value
  _, contours, hierarchy = cv2.findContours(
    thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

  # sort contours by largest volume
  contours = sorted(contours, key=cv2.contourArea, reverse=True)

  shapes = []
  for i in range(min(3, len(contours))):
    rectangle = cv2.minAreaRect(contours[i])
    corners = cv2.boxPoints(rectangle)
    corners = rectify(corners, portrait=True)
    # corners = expand_points(corners, 15)

    # writes dots for corners of bounding boxes on original image
    # for point in corners:
      # cv2.circle(orig_im, (point[0], point[1]), 0, (0,255,0), im.shape[0]/100)

    # create an image of just the shape
    h = np.array([ 
      [0,0],
      [out_w-1,0],
      [out_w-1,out_h-1],
      [0,out_h-1]
    ],np.float32)
    transform = cv2.getPerspectiveTransform(corners,h)
    warp = cv2.warpPerspective(orig_im,transform,(out_w,out_h))
    if display_shapes:
      display_im(warp)
    shapes.append(warp)

  return shapes

def write_shape_with_label(shape, input_card_path, out_dir=SHAPES_OUT_DIR):
  """Cut path name up to extract the label minus the number, write the
  shape to: <out_dir>/<color>-<shade>-<shape>.jpg"""
  if not os.path.exists(out_dir):
    os.mkdir(out_dir)
  tokens = input_card_path.split('/')[-1].split('-')
  tokens[1] = 'single'
  new_filename = '-'.join(tokens)
  print(new_filename)
  write_im(shape, new_filename, out_dir=out_dir)

def main():
  card_file = sys.argv[1]
  shapes = find_shapes(card_file, display_shapes=False)
  write_shape_with_label(shapes[0], card_file)

if __name__ == "__main__":
  main()
