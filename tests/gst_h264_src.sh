gst-launch-1.0 -v tcpclientsrc host=$1 port=$2  \
    ! gdpdepay ! rtph264depay ! avdec_h264 ! videoconvert \
    ! autovideosink sync=false
