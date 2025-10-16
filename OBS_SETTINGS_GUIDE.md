# OBS Studio Settings for Social Media Optimization

## 🎯 **Recommended OBS Settings for Best Results**

### **Video Settings**
- **Base Resolution**: 1080x1920 (9:16 aspect ratio)
- **Output Resolution**: 1080x1920 (same as base)
- **FPS**: 30 or 60 (30 recommended for most content)
- **Bitrate**: 3000-4000 kbps (3-4 Mbps)

### **Audio Settings**
- **Sample Rate**: 48 kHz
- **Channels**: Stereo (2 channels)
- **Bitrate**: 128 kbps or higher
- **Codec**: AAC

### **Recording Settings**
- **Format**: MP4
- **Encoder**: x264 (software) or NVENC (hardware)
- **Rate Control**: CBR (Constant Bitrate)
- **Keyframe Interval**: 2 seconds

## 📱 **Platform-Specific Requirements**

### **Instagram Reels**
- **Resolution**: 1080x1920 (minimum 540x960)
- **Duration**: 3-90 seconds
- **Aspect Ratio**: 9:16 (vertical)
- **File Size**: Under 100MB
- **Codec**: H.264 video, AAC audio

### **YouTube Shorts**
- **Resolution**: 1080x1920 (minimum 720x1280)
- **Duration**: 1-60 seconds
- **Aspect Ratio**: 9:16 (vertical)
- **File Size**: Under 2GB
- **Codec**: H.264 video, AAC audio

### **TikTok**
- **Resolution**: 1080x1920 (minimum 720x1280)
- **Duration**: 1-180 seconds
- **Aspect Ratio**: 9:16 (vertical)
- **File Size**: Under 4GB
- **Codec**: H.264 video, AAC audio

## ⚙️ **OBS Studio Configuration Steps**

### 1. **Set Up Canvas**
1. Open OBS Studio
2. Go to **Settings** → **Video**
3. Set **Base (Canvas) Resolution**: `1080x1920`
4. Set **Output (Scaled) Resolution**: `1080x1920`
5. Set **FPS**: `30` or `60`

### 2. **Configure Recording**
1. Go to **Settings** → **Output**
2. Set **Output Mode**: `Advanced`
3. Set **Recording Format**: `mp4`
4. Set **Encoder**: `x264` or `NVENC`
5. Set **Rate Control**: `CBR`
6. Set **Bitrate**: `3000` (3 Mbps)

### 3. **Audio Settings**
1. Go to **Settings** → **Audio**
2. Set **Sample Rate**: `48 kHz`
3. Set **Channels**: `Stereo`
4. Set **Desktop Audio Bitrate**: `128`
5. Set **Mic/Auxiliary Audio Bitrate**: `128`

### 4. **Advanced Settings**
1. Go to **Settings** → **Advanced**
2. Set **Process Priority**: `High`
3. Set **Color Format**: `NV12`
4. Set **Color Space**: `709`
5. Set **Color Range**: `Partial`

## 🎬 **Scene Setup for Vertical Content**

### **Recommended Scene Layout**
1. **Main Content**: Center of screen (720x1280 area)
2. **Safe Zones**: Leave 180px margins on left/right
3. **Text Overlay**: Keep within safe zone
4. **Background**: Solid color or subtle pattern

### **Sources to Add**
1. **Display Capture** or **Window Capture** for screen recording
2. **Video Capture Device** for webcam (if needed)
3. **Text** for titles/overlays
4. **Image** for logos/branding
5. **Audio Input Capture** for microphone

## 🔧 **Optimization Tips**

### **For Better Performance**
- Use **NVENC** encoder if you have an NVIDIA GPU
- Set **Process Priority** to **High**
- Close unnecessary applications
- Use **CBR** rate control for consistent quality

### **For Better Quality**
- Use **x264** encoder with **CRF 18-23**
- Set **Keyframe Interval** to **2 seconds**
- Use **High** preset for x264
- Ensure good lighting for webcam

### **For File Size Management**
- Use **CBR** with **3000 kbps** for good quality/size balance
- Avoid recording longer than needed
- Use **Hardware encoding** when available

## 🚀 **Quick Setup Checklist**

- [ ] Canvas resolution: 1080x1920
- [ ] Output resolution: 1080x1920
- [ ] FPS: 30
- [ ] Bitrate: 3000 kbps
- [ ] Audio: 48 kHz, Stereo, 128 kbps
- [ ] Format: MP4
- [ ] Encoder: x264 or NVENC
- [ ] Rate Control: CBR

## 📊 **Testing Your Setup**

After configuring OBS:
1. Record a short test video (10-15 seconds)
2. Check the file properties:
   - Resolution should be 1080x1920
   - Duration should be correct
   - File size should be reasonable
3. Test with the AI Content Creation tool
4. Verify compliance with platform requirements

## 🆘 **Troubleshooting**

### **Common Issues**
- **Resolution too low**: Increase canvas resolution
- **Video too short**: Record longer content (minimum 3s for Instagram)
- **File too large**: Reduce bitrate or duration
- **Poor quality**: Increase bitrate or use better encoder settings
- **Audio issues**: Check sample rate and bitrate settings

### **Performance Issues**
- Use hardware encoding (NVENC/QuickSync)
- Lower resolution if needed (720x1280 minimum)
- Close other applications
- Check CPU/GPU usage




