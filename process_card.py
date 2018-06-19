#!/usr/bin/env python
"""Process a card image to make it easier to match an unlabeled card to
the correct labeled card."""

import os
import sys
import cv2
from common import PROCESS_CARD_OUT_DIR, write_im, display_im

from vendor import noteshrink

PROCESSED_CARD_FILENAME = 'processed.jpg'

def to_pil(cv2_im):
  pass

def to_cv2(pil_im):
  pass

def blur_card(card_filename):
  im = cv2.imread(card_filename, 1)

  # filters to make it easier for opencv to find card
  blur = cv2.GaussianBlur(im,(3,1),1)
  filename = "%s_blurred.png" % (card_filename)
  cv2.imwrite(filename, blur)

  display_im(blur)

  return filename

def process_card(card_filename):
  """Process a card: #TODO for what this means, but probably at least
  bucketing colors.
  """
  # TODO
  blurred = blur_card(card_filename)
  shrunk_card = noteshrink_card(blurred)
  keypoints_card(shrunk_card)
  return


def keypoints_card(card_file_to_classify):
  import numpy as np
  import cv2
  from matplotlib import pyplot as plt
  img = cv2.imread(card_file_to_classify,0)
  # Initiate ORB detector
  orb = cv2.ORB_create()
  # find the keypoints with ORB
  kp = orb.detect(img,None)
  # compute the descriptors with ORB
  kp, des = orb.compute(img, kp)
  # draw only keypoints location,not size and orientation
  img2 = cv2.drawKeypoints(img, kp, None, color=(0,255,0), flags=0)
  plt.imshow(img2), plt.show()

def noteshrink_card(card_filename):
  img, dpi = noteshrink.load(card_filename)
  options = noteshrink.get_argument_parser().parse_args()
  options.num_colors = 10

  if img is None:
      return

  output_filename = "%s.out.png" % (card_filename)

  samples = noteshrink.sample_pixels(img, options)
  palette = noteshrink.get_palette(samples, options)

  labels = noteshrink.apply_palette(img, palette, options)

  print "SAVING", output_filename
  noteshrink.save(output_filename, labels, palette, dpi, options)
  cv2_im = cv2.imread(output_filename, 1)
  return output_filename



def main():

  for unprocessed_card_file in sys.argv[1:]:
    unprocessed_card = cv2.imread(unprocessed_card_file, 1)
    processed_card = process_card(unprocessed_card_file)
    write_im(processed_card, PROCESSED_CARD_FILENAME, PROCESS_CARD_OUT_DIR)

if __name__ == "__main__":
  main()