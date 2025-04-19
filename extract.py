'''
1. color segmentation: separate the fabric from background
    color threshold for just the white fabric
    find the outer edges... how? -- > turns out there's a contour flag for this!
    or look for lines that are not contained by any combination of the other lines
    using canny, but that assumes rectangle fabric.
2. color segmentation: separate the cutout from the fabric
    easy, just thresholding. get a binary mask of the fabric.
4. scale using nickel for reference.
    i guess combined color and circle detection? can do basic color thresholding for now
5. determine the remaining area of the fabric. with scale this should be somewhat
    straightforward i think? can use a pixels-to-inches sort of thing
5. use some sort of packing algorithm on the leftover fabric? or even just
    cleave out the vertical strip with the cutout, like based on leftmost/rightmost
    points on cutout. (bounding box, basically.)
'''

