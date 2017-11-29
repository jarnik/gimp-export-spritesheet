#!/usr/bin/env python

import os
from gimpfu import *

import gimpenums

from pygimplib import pgpdb

#http://doc.starling-framework.org/v2.1/starling/textures/TextureAtlas.html

def export_spritesheet(image, layer, outputFolder):
  ''' Save the current layer into a PNG file, a JPEG file and a BMP file.
    
  Parameters:
  image : image The current image.
  layer : layer The layer of the image that is selected.
  outputFolder : string The folder in which to save the images.
  '''

  spritesheetName = os.path.splitext(image.name)[0]
  atlasImageFilename = "%s.png" % (spritesheetName)
  outputPath = outputFolder + "\\"+ atlasImageFilename
  atlasPath = outputFolder + "\\"+ "%s.xml" % (spritesheetName)

  atlas = open(atlasPath,"w") 
  atlas.write("<TextureAtlas imagePath='"+atlasImageFilename+"'>\n")  

  spritesheet = pgpdb.duplicate(image, metadata_only=True)

  spriteCount = 0
  for i in range(len(image.layers)):
    if not image.layers[i].visible:
      # ignore invisible layers
      continue
    if not(image.layers[i].name.startswith('[') and image.layers[i].name.endswith(']')):
      spriteCount += 1
  cols = math.ceil(math.sqrt(spriteCount))

  x = 0
  y = 0
  imageWidth = 0
  imageHeight = 0
  exportedLayers = 0
  spritesInRow = 0
  for i in range(len(image.layers)):
    if not image.layers[i].visible:
      # ignore invisible layers
      continue
    if not(image.layers[i].name.startswith('[') and image.layers[i].name.endswith(']')):
      layer_copy = pdb.gimp_layer_new_from_drawable(image.layers[i], spritesheet)
      pdb.gimp_image_insert_layer(spritesheet, layer_copy, None, exportedLayers)
      # This is necessary for file formats which flatten the image (such as JPG).
      pdb.gimp_item_set_visible(layer_copy, True)

      pdb.gimp_layer_set_offsets(spritesheet.layers[exportedLayers],x,y) #offset layers
      layerWidth = image.layers[i].width
      layerHeight = image.layers[i].height
      layerName = image.layers[i].name
      atlas.write("  <SubTexture name='%s' x='%d' y='%d' width='%d' height='%d'/>\n" % (
        layerName, x, y, layerWidth, layerHeight
      ))
      x += layerWidth
      imageWidth = max(imageWidth,x)
      imageHeight = max(imageHeight,y+layerHeight)
      exportedLayers += 1
      spritesInRow += 1
      if spritesInRow >= cols:
        spritesInRow = 0
        x = 0
        y += layerHeight

  exportedBackgrounds = 0
  for i in range(len(image.layers)):
    if not image.layers[i].visible:
      # ignore invisible layers
      continue
    if image.layers[i].name.startswith('[') and image.layers[i].name.endswith(']'):      
      for j in range(exportedLayers):
        layer_copy = pdb.gimp_layer_new_from_drawable(image.layers[i], spritesheet)
        pdb.gimp_image_insert_layer(spritesheet, layer_copy, None, exportedLayers + exportedBackgrounds)
        offsets = spritesheet.layers[exportedBackgrounds].offsets
        pdb.gimp_layer_set_offsets(spritesheet.layers[exportedLayers + exportedBackgrounds],offsets[0],offsets[1]) #offset layers        
        exportedBackgrounds += 1    

  atlas.write("</TextureAtlas>\n") 
  atlas.close()

  pdb.gimp_image_resize(spritesheet,imageWidth,imageHeight,0,0)

  # flattening would kill the alpha
  layer = pdb.gimp_image_merge_visible_layers(spritesheet, gimpenums.CLIP_TO_IMAGE)

  pdb.file_png_save(spritesheet, spritesheet.layers[0], outputPath, outputPath, 0, 9, 0, 0, 0, 0, 0)
  pdb.gimp_image_delete(spritesheet)

register(
  "python_fu_export_spritesheet",
  "Export spritesheet",
  "Export spritesheet.",
  "jarnik",
  "BSD",
  "2017",
  "<Image>/File/Export/Export Spritesheet",
  "*",
  [ 
    (PF_DIRNAME, "outputFolder", "Output directory", "/tmp"),
  ],
  [],
  export_spritesheet)

main() 