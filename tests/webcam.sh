gst-launch-0.10 v4l2src device=/dev/video1 ! video/x-raw-rgb, width=864, height=480 \
	! queue ! ffmpegcolorspace ! ximagesink
