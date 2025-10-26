# Tron Lightbike Transition Generation with Sora 2

This guide explains how to use the new Sora 2 integration to generate realistic Tron lightbike transition sequences for your content creation pipeline.

## 🚀 Quick Start

### 1. Test Basic Generation

```bash
# Test with a simple prompt
uv run gen.py -p "A cool cat on a motorcycle in the night"

# Test with a Tron lightbike prompt
uv run gen.py -p "A sleek neon blue lightbike racing through a digital grid at incredible speed, leaving glowing trails, cyberpunk aesthetic"
```

### 2. Generate Transitions via CLI

```bash
# Generate racing-style transitions
uv run content-cli transitions generate -t racing -c 3

# Generate custom transition
uv run content-cli transitions generate -p "Your custom prompt here"

# List all generated transitions
uv run content-cli transitions list

# Check status of specific video
uv run content-cli transitions status <video_id>
```

## 🎬 Transition Types

### Racing Transitions
High-speed lightbike racing sequences with dramatic motion and neon trails.

```bash
uv run content-cli transitions generate -t racing -c 5
```

**Example prompts:**
- Lightbikes racing through digital highways
- High-speed chases with sparks flying
- Gravity-defying jumps over digital chasms
- Formation racing through glowing tunnels

### Transition Effects
Smooth morphing and transformation sequences.

```bash
uv run content-cli transitions generate -t transitions -c 3
```

**Example prompts:**
- Lightbikes materializing from digital particles
- Seamless digital transformations
- Morphing through geometric shapes
- Digital replication effects

### Environmental Transitions
Atmospheric sequences with rich cyberpunk environments.

```bash
uv run content-cli transitions generate -t environmental -c 4
```

**Example prompts:**
- Racing through neon-lit cityscapes
- Navigating digital forests
- Ascending spiral digital towers
- Racing through tunnels of pure light

## 🛠️ Advanced Usage

### Custom Configuration

```python
from content_creation.sora_transitions import SoraTransitionGenerator, TransitionConfig

# Create custom configuration
config = TransitionConfig(
    style="tron_lightbike",
    duration=10,  # 10 seconds
    resolution="1920x1080",
    fps=30,
    quality="high"
)

# Generate with custom config
generator = SoraTransitionGenerator("my_transitions")
transition = generator.generate_transition(
    "Your custom prompt",
    "custom",
    config
)
```

### Batch Generation

```python
# Generate multiple transitions of different types
generator = SoraTransitionGenerator()

# Racing sequences
racing_transitions = generator.generate_transition_batch("racing", count=3)

# Environmental sequences  
env_transitions = generator.generate_transition_batch("environmental", count=2)

# Custom transitions
custom_prompts = [
    "Lightbike racing through a digital storm",
    "Neon bike performing a barrel roll through space",
    "Digital bike splitting into multiple copies"
]

for prompt in custom_prompts:
    transition = generator.generate_transition(prompt, "custom")
    print(f"Generated: {transition.video_id}")
```

## 📁 File Organization

Generated transitions are organized in the following structure:

```
generated_transitions/
├── racing/
│   ├── video_123_metadata.json
│   └── video_456_metadata.json
├── transitions/
│   └── video_789_metadata.json
├── environmental/
│   └── video_101_metadata.json
└── custom/
    └── video_202_metadata.json
```

Each metadata file contains:
- Video ID and status
- Original prompt used
- Creation timestamp
- Transition type
- File path (when available)

## 🎯 Integration with Video Processing

The transition generation can be integrated with your existing video processing pipeline:

```python
from content_creation.sora_transitions import SoraTransitionGenerator
from content_creation.video_processor import VideoProcessor

# Generate transition
generator = SoraTransitionGenerator()
transition = generator.generate_transition("Your prompt")

# Process the generated video when ready
processor = VideoProcessor()
# ... process the transition video
```

## 🔧 Configuration

### Environment Variables

Make sure you have your OpenAI API key set:

```bash
# In your .env file
OPENAI_API_KEY=your_api_key_here
```

### Output Directory

You can specify custom output directories:

```bash
# Custom output directory
uv run content-cli transitions generate -t racing -o /path/to/transitions

# Or in Python
generator = SoraTransitionGenerator("/custom/path")
```

## 📊 Monitoring and Status

### Check Generation Status

```bash
# List all transitions
uv run content-cli transitions list

# List specific type
uv run content-cli transitions list -t racing

# Check specific video status
uv run content-cli transitions status video_123
```

### Programmatic Status Checking

```python
generator = SoraTransitionGenerator()

# Get all transitions
all_transitions = generator.list_generated_transitions()

# Get by type
racing_transitions = generator.list_generated_transitions("racing")

# Check specific video
status = generator.get_transition_status("video_123")
if status:
    print(f"Status: {status['status']}")
```

## 🎨 Prompt Engineering Tips

### Effective Tron Lightbike Prompts

1. **Be specific about visual elements:**
   - "neon blue lightbike" (not just "bike")
   - "glowing trails" or "digital particles"
   - "cyberpunk aesthetic" or "futuristic"

2. **Include motion descriptors:**
   - "racing at incredible speed"
   - "gravity-defying jump"
   - "smooth morphing transition"

3. **Specify lighting and atmosphere:**
   - "neon-lit cityscape"
   - "dramatic lighting"
   - "cinematic lighting"

4. **Add environmental context:**
   - "digital grid"
   - "cyberpunk cityscape"
   - "neon tunnel"

### Example High-Quality Prompts

```
"A sleek neon blue lightbike racing through a dark digital grid at incredible speed, leaving glowing trails that pulse with energy, cyberpunk aesthetic, futuristic racing scene, cinematic lighting"

"Two lightbikes in a high-speed chase through a neon-lit digital highway, sparks flying from their wheels, dramatic lighting, Tron-style racing, motion blur effects"

"A lightbike performing a gravity-defying jump over a digital chasm, neon trails arcing through the void, cinematic lighting, cyberpunk atmosphere"
```

## 🚨 Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   ❌ Error: OPENAI_API_KEY environment variable not set
   ```
   Solution: Set your OpenAI API key in the `.env` file

2. **Rate Limiting**
   ```
   ⏳ Waiting 2 seconds before next generation...
   ```
   This is normal - the system automatically adds delays between requests

3. **Generation Failures**
   - Check your internet connection
   - Verify your OpenAI API key has sufficient credits
   - Try with a simpler prompt first

### Getting Help

- Check the generated metadata files for error details
- Use `uv run content-cli transitions list` to see all generated content
- Monitor the console output for detailed error messages

## 🎉 Examples

Run the complete demo to see all features in action:

```bash
uv run examples/tron_transitions.py
```

This will generate sample transitions of each type and demonstrate the management features.
