"""
Generate a complete system architecture diagram in PNG format using matplotlib
"""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import matplotlib.lines as mlines

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(16, 20))
ax.set_xlim(0, 10)
ax.set_ylim(0, 24)
ax.axis('off')

# Title
ax.text(5, 23.5, 'SymptomSense Health AI - Complete Architecture', 
        ha='center', va='top', fontsize=20, fontweight='bold')

# Color scheme
color_user = '#E8F5E9'
color_frontend = '#BBDEFB'
color_backend = '#FFE0B2'
color_external = '#F8BBD0'
color_arrow = '#666666'

def draw_box(ax, x, y, width, height, text, color, fontsize=10, fontweight='normal'):
    """Draw a rounded box with text"""
    box = FancyBboxPatch((x, y), width, height,
                         boxstyle="round,pad=0.1",
                         edgecolor='black',
                         facecolor=color,
                         linewidth=1.5)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text,
            ha='center', va='center',
            fontsize=fontsize, fontweight=fontweight,
            wrap=True)

def draw_arrow(ax, x1, y1, x2, y2, label='', style='->'):
    """Draw an arrow with optional label"""
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle=style,
                           color=color_arrow,
                           linewidth=2,
                           mutation_scale=20)
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x + 0.3, mid_y, label,
                fontsize=8, style='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

# ===== USER LAYER =====
draw_box(ax, 3.5, 21.5, 3, 1, 'User Browser\n(localhost:3000)', color_user, 11, 'bold')

# ===== FRONTEND LAYER =====
# Main frontend container
draw_box(ax, 0.5, 16, 9, 5, '', color_frontend, 10)
ax.text(5, 20.7, 'React Frontend (Vite + TypeScript)', ha='center', fontsize=12, fontweight='bold')

# Pages
draw_box(ax, 0.8, 18.5, 2.5, 2, 'Pages\n\n• Landing\n• Login\n• Dashboard\n• Assessment\n• Results\n• History\n• Profile', 
         'white', 9)

# Components
draw_box(ax, 3.6, 18.5, 2.5, 2, 'Components\n\n• Header\n• Sidebar\n• Results\n• Treatment\n• Forms', 
         'white', 9)

# State Management
draw_box(ax, 6.4, 18.5, 2.5, 2, 'Zustand Stores\n\n• Auth\n• User\n• Assessment\n• System', 
         'white', 9)

# Services
draw_box(ax, 0.8, 16.3, 4, 1.8, 'Firebase Service\n\n• login()\n• logout()\n• getToken()', 
         'white', 9)
draw_box(ax, 5.1, 16.3, 3.8, 1.8, 'API Service (Axios)\n\n• get() • post() • put()', 
         'white', 9)

# ===== BACKEND LAYER =====
# Main backend container
draw_box(ax, 0.5, 7.5, 9, 8, '', color_backend, 10)
ax.text(5, 15.2, 'Django Backend (localhost:8000)', ha='center', fontsize=12, fontweight='bold')

# API Endpoints
draw_box(ax, 0.8, 13.5, 3.5, 1.3, 'REST API Endpoints\n\n/api/health/ • /api/status/\n/api/user/profile/ • /api/assess/', 
         'white', 9)

# Agent System
draw_box(ax, 4.6, 13.5, 4.3, 1.3, 'Agent System\n\nOrchestrator • Validation\nPredictor • Explanation\nRecommendation • Extraction', 
         'white', 9)

# ML Pipeline
draw_box(ax, 0.8, 11.8, 3.5, 1.3, 'ML Pipeline\n\nPyTorch Model\n• Inference\n• Preprocessing', 
         'white', 9)

# Backend Services
draw_box(ax, 4.6, 11.8, 4.3, 1.3, 'Backend Services\n\nFirebase Auth • Firebase DB\nGemini Client', 
         'white', 9)

# Treatment & Knowledge Base
draw_box(ax, 0.8, 10.2, 3.5, 1.3, 'Treatment System\n\nKnowledge Base\n• Allopathy • Ayurveda\n• Homeopathy • Lifestyle', 
         'white', 9)

# Common Utilities
draw_box(ax, 4.6, 10.2, 4.3, 1.3, 'Common Utilities\n\nCache Service\nError Handling\nThrottling', 
         'white', 9)

# Data Layer
draw_box(ax, 0.8, 8, 8.1, 1.8, 'Data Layer\n\nFirestore Collections: users/ • assessments/ • profiles/ • history/', 
         'white', 9)

# ===== EXTERNAL SERVICES =====
# Firebase
draw_box(ax, 0.5, 4.5, 4, 2.5, '', color_external, 10)
ax.text(2.5, 6.7, 'Firebase Cloud', ha='center', fontsize=11, fontweight='bold')
draw_box(ax, 0.8, 5.2, 3.4, 0.7, 'Authentication\n(Google OAuth)', 'white', 9)
draw_box(ax, 0.8, 4.8, 3.4, 0.7, 'Firestore Database', 'white', 9)

# Gemini AI
draw_box(ax, 5.5, 4.5, 4, 2.5, '', color_external, 10)
ax.text(7.5, 6.7, 'Google Gemini AI', ha='center', fontsize=11, fontweight='bold')
draw_box(ax, 5.8, 5.2, 3.4, 0.7, 'AI Explanations', 'white', 9)
draw_box(ax, 5.8, 4.8, 3.4, 0.7, 'Data Extraction & Validation', 'white', 9)

# ===== ARROWS / DATA FLOW =====
# User to Frontend
draw_arrow(ax, 5, 21.5, 5, 21, 'HTTP Requests')

# Frontend internal
draw_arrow(ax, 2, 18.5, 2, 18.1, '')
draw_arrow(ax, 5, 18.5, 5, 18.1, '')
draw_arrow(ax, 7.5, 18.5, 7.5, 18.1, '')

# Frontend to Backend
draw_arrow(ax, 7, 16, 7, 15.5, 'HTTP + JWT')

# Frontend to Firebase
draw_arrow(ax, 2.5, 16.3, 2.5, 7, 'Auth')

# Backend API to Agents
draw_arrow(ax, 4.3, 13.5, 4.6, 13.5, '')

# Agents to ML
draw_arrow(ax, 4.6, 12.5, 4.3, 12.5, '')

# Backend to Services
draw_arrow(ax, 6.5, 11.8, 6.5, 9.8, '')

# Backend to Firebase
draw_arrow(ax, 2.5, 7.5, 2.5, 7, '')

# Backend to Gemini
draw_arrow(ax, 7.5, 7.5, 7.5, 7, '')

# ===== LEGEND =====
legend_y = 2.5
ax.text(5, legend_y + 1, 'Technology Stack', ha='center', fontsize=12, fontweight='bold')

legend_items = [
    ('Frontend:', 'React 18 • TypeScript • Vite • Zustand • MUI • Axios'),
    ('Backend:', 'Django 4.2 • DRF • Python 3.8+ • PyTorch'),
    ('Cloud:', 'Firebase Auth & Firestore • Google Gemini AI'),
    ('Security:', 'JWT Tokens • CORS • Rate Limiting • Input Validation')
]

y_pos = legend_y + 0.3
for title, tech in legend_items:
    ax.text(1, y_pos, title, fontsize=9, fontweight='bold')
    ax.text(2.2, y_pos, tech, fontsize=9)
    y_pos -= 0.4

# ===== KEY FEATURES =====
features_y = 0.5
ax.text(5, features_y + 0.8, 'Key Features', ha='center', fontsize=12, fontweight='bold')
features = '• Multi-Agent AI System  • ML-Powered Predictions  • Real-time Health Assessment\n• Treatment Recommendations (4 Systems)  • Secure Authentication  • Rate-Limited API'
ax.text(5, features_y + 0.2, features, ha='center', fontsize=9)

# Save figure
plt.tight_layout()
plt.savefig('architecture_diagram.png', dpi=300, bbox_inches='tight', facecolor='white')
print("✓ Architecture diagram generated successfully!")
print("✓ Output file: architecture_diagram.png")
print("✓ Resolution: 300 DPI")
