#!/usr/bin/env python3
"""
Generate Black & White System Architecture Diagram
Professional grayscale diagram suitable for printing and documentation
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle, Polygon
import matplotlib.lines as mlines
import os

# Create figure
fig = plt.figure(figsize=(28, 36), facecolor='white')
ax = fig.add_subplot(111)
ax.set_xlim(0, 28)
ax.set_ylim(0, 36)
ax.axis('off')

# Black & White color scheme
COLORS = {
    'black': '#000000',
    'dark_gray': '#333333',
    'medium_gray': '#666666',
    'light_gray': '#999999',
    'very_light_gray': '#CCCCCC',
    'white': '#FFFFFF',
    'border': '#000000',
    'text': '#000000',
    'bg': '#F5F5F5'
}

def draw_zone_box(ax, x, y, width, height, title, pattern='solid'):
    """Draw a zone box with different patterns"""
    # Main box
    if pattern == 'solid':
        box = Rectangle((x, y), width, height,
                       facecolor=COLORS['very_light_gray'],
                       edgecolor=COLORS['black'],
                       linewidth=3)
    elif pattern == 'light':
        box = Rectangle((x, y), width, height,
                       facecolor=COLORS['white'],
                       edgecolor=COLORS['black'],
                       linewidth=3)
    elif pattern == 'medium':
        box = Rectangle((x, y), width, height,
                       facecolor=COLORS['very_light_gray'],
                       edgecolor=COLORS['black'],
                       linewidth=3,
                       linestyle='--')
    else:
        box = Rectangle((x, y), width, height,
                       facecolor=COLORS['white'],
                       edgecolor=COLORS['black'],
                       linewidth=3)
    
    ax.add_patch(box)
    
    # Title bar
    title_box = Rectangle((x, y + height - 1.5), width, 1.5,
                          facecolor=COLORS['dark_gray'],
                          edgecolor=COLORS['black'],
                          linewidth=3)
    ax.add_patch(title_box)
    
    ax.text(x + width/2, y + height - 0.75, title,
           ha='center', va='center', fontsize=14,
           fontweight='bold', color=COLORS['white'])

def draw_component_box(ax, x, y, width, height, title, subtitle='', items=None, style='solid'):
    """Draw a component box"""
    # Main box with different styles
    if style == 'solid':
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle="round,pad=0.1",
                            facecolor=COLORS['white'],
                            edgecolor=COLORS['black'],
                            linewidth=2.5)
    elif style == 'dashed':
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle="round,pad=0.1",
                            facecolor=COLORS['white'],
                            edgecolor=COLORS['medium_gray'],
                            linewidth=2.5,
                            linestyle='--')
    else:
        box = FancyBboxPatch((x, y), width, height,
                            boxstyle="round,pad=0.1",
                            facecolor=COLORS['very_light_gray'],
                            edgecolor=COLORS['black'],
                            linewidth=2.5)
    
    ax.add_patch(box)
    
    # Title
    ax.text(x + width/2, y + height - 0.4, title,
           ha='center', va='center', fontsize=11,
           fontweight='bold', color=COLORS['black'])
    
    # Subtitle
    if subtitle:
        ax.text(x + width/2, y + height - 0.8, subtitle,
               ha='center', va='center', fontsize=8,
               style='italic', color=COLORS['dark_gray'])
    
    # Items
    if items:
        item_y = y + height - 1.3
        for item in items:
            ax.text(x + 0.2, item_y, f'• {item}',
                   ha='left', va='top', fontsize=7,
                   color=COLORS['dark_gray'])
            item_y -= 0.3

def draw_arrow(ax, x1, y1, x2, y2, label='', style='solid', width=2):
    """Draw connection arrow"""
    if style == 'dashed':
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='-|>',
                               mutation_scale=25,
                               linewidth=width,
                               color=COLORS['black'],
                               linestyle='--')
    else:
        arrow = FancyArrowPatch((x1, y1), (x2, y2),
                               arrowstyle='-|>',
                               mutation_scale=25,
                               linewidth=width,
                               color=COLORS['black'])
    
    ax.add_patch(arrow)
    
    if label:
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mid_x, mid_y + 0.3, label,
               ha='center', va='bottom', fontsize=7,
               fontweight='bold', color=COLORS['black'],
               bbox=dict(boxstyle='round,pad=0.3',
                        facecolor=COLORS['white'],
                        edgecolor=COLORS['black'],
                        linewidth=1))

def draw_icon_circle(ax, x, y, radius, label):
    """Draw icon circle with label"""
    circle = Circle((x, y), radius,
                   facecolor=COLORS['white'],
                   edgecolor=COLORS['black'],
                   linewidth=2)
    ax.add_patch(circle)
    
    ax.text(x, y, label,
           ha='center', va='center', fontsize=10,
           fontweight='bold', color=COLORS['black'])

# ============================================================================
# HEADER
# ============================================================================
# Title
ax.text(14, 35, 'SymptomSense Health AI Platform',
       ha='center', va='center', fontsize=26,
       fontweight='bold', color=COLORS['black'])
ax.text(14, 34.3, 'System Architecture Diagram',
       ha='center', va='center', fontsize=16,
       color=COLORS['dark_gray'])

# Subtitle
ax.text(14, 33.6, 'Three-Tier Architecture with Multi-Agent System',
       ha='center', va='center', fontsize=11,
       style='italic', color=COLORS['medium_gray'])

# Metadata box
metadata_box = Rectangle((22, 33), 5, 2.5,
                         facecolor=COLORS['white'],
                         edgecolor=COLORS['black'],
                         linewidth=2)
ax.add_patch(metadata_box)
ax.text(24.5, 34.8, 'Architecture v2.0',
       ha='center', va='center', fontsize=10,
       fontweight='bold')
ax.text(22.5, 34.3, 'Type: System Architecture',
       ha='left', va='center', fontsize=8)
ax.text(22.5, 33.9, 'Format: Black & White',
       ha='left', va='center', fontsize=8)
ax.text(22.5, 33.5, 'Date: February 2024',
       ha='left', va='center', fontsize=8)
ax.text(22.5, 33.1, 'Status: Production',
       ha='left', va='center', fontsize=8)

# ============================================================================
# TIER 1: CLIENT / PRESENTATION LAYER
# ============================================================================
draw_zone_box(ax, 1, 27, 26, 5, 'TIER 1: CLIENT / PRESENTATION LAYER', 'light')

# Web Application
draw_component_box(ax, 2, 28.5, 5, 3,
                  'Web Application',
                  'React 18 + TypeScript',
                  ['Vite Build System', 'Material-UI Components', 'Zustand State Management', 'React Router v6'],
                  'solid')

# Mobile Responsive
draw_component_box(ax, 8, 28.5, 5, 3,
                  'Mobile Responsive',
                  'Progressive Web App',
                  ['Responsive Design', 'Touch Optimized', 'Offline Capable', 'Push Notifications'],
                  'solid')

# User Interface
draw_component_box(ax, 14, 28.5, 5, 3,
                  'User Interface',
                  'Component Library',
                  ['Assessment Forms', 'Results Dashboard', 'Report Upload', 'Treatment Plans'],
                  'solid')

# Authentication UI
draw_component_box(ax, 20, 28.5, 5, 3,
                  'Authentication UI',
                  'Firebase Auth',
                  ['OAuth 2.0', 'JWT Tokens', 'Session Management', 'Role-Based Access'],
                  'solid')

# ============================================================================
# TIER 2: APPLICATION LAYER
# ============================================================================
draw_zone_box(ax, 1, 11, 26, 15, 'TIER 2: APPLICATION / BUSINESS LOGIC LAYER', 'solid')

# API Gateway
draw_component_box(ax, 2, 23, 6, 2.5,
                  'API Gateway',
                  'Django REST Framework',
                  ['RESTful Endpoints', 'Rate Limiting', 'CORS Protection', 'Request Validation'],
                  'solid')

# Arrow from Client to API
draw_arrow(ax, 14, 27, 5, 25.5, 'HTTPS/TLS 1.3', 'solid', 2.5)

# Orchestrator Agent
draw_component_box(ax, 10, 23, 8, 2.5,
                  'Orchestrator Agent',
                  'Workflow Coordinator',
                  ['Pipeline Management', 'Agent Coordination', 'Context Management', 'Error Handling'],
                  'shaded')

# Arrow from API to Orchestrator
draw_arrow(ax, 8, 24, 10, 24, '', 'solid', 2)

# Multi-Agent System Box
agent_box = Rectangle((2, 12.5), 24, 9.5,
                      facecolor=COLORS['very_light_gray'],
                      edgecolor=COLORS['black'],
                      linewidth=2,
                      linestyle='--')
ax.add_patch(agent_box)
ax.text(14, 21.5, 'MULTI-AGENT SYSTEM',
       ha='center', va='center', fontsize=12,
       fontweight='bold', color=COLORS['black'])

# Validation Agent
draw_component_box(ax, 3, 18.5, 5, 2.5,
                  'Validation Agent',
                  'Input Sanitization',
                  ['Data Type Checks', 'Range Validation', 'AI Validation', 'Sanitization'],
                  'solid')

# Predictor Agent
draw_component_box(ax, 9, 18.5, 5, 2.5,
                  'Predictor Agent',
                  'ML Predictions',
                  ['Feature Extraction', 'Neural Network', 'Top-5 Predictions', 'Confidence Scores'],
                  'solid')

# Explanation Agent
draw_component_box(ax, 15, 18.5, 5, 2.5,
                  'Explanation Agent',
                  'AI Explanations',
                  ['Gemini Integration', 'Medical Context', 'Natural Language', 'User-Friendly'],
                  'solid')

# Recommendation Agent
draw_component_box(ax, 3, 15, 5, 2.5,
                  'Recommendation Agent',
                  'Treatment Plans',
                  ['Allopathy', 'Ayurveda', 'Homeopathy', 'Personalized'],
                  'solid')

# Extraction Agent
draw_component_box(ax, 9, 15, 5, 2.5,
                  'Extraction Agent',
                  'Report Processing',
                  ['OCR/PDF Parse', 'Data Extraction', 'Field Mapping', 'Validation'],
                  'solid')

# Severity Agent
draw_component_box(ax, 15, 15, 5, 2.5,
                  'Severity Agent',
                  'Risk Assessment',
                  ['Severity Calculation', 'Red Flag Detection', 'Urgency Level', 'Care Recommendations'],
                  'solid')

# ML Engine
draw_component_box(ax, 21, 15, 5, 6,
                  'ML Engine',
                  'PyTorch Neural Network',
                  ['3-Layer Architecture', '512-256-128 Neurons', 'Dropout 30%', 'BCE Loss', 'Adam Optimizer', '87.3% Accuracy'],
                  'shaded')

# Arrows from Orchestrator to Agents
draw_arrow(ax, 14, 23, 5.5, 21, '', 'dashed', 1.5)
draw_arrow(ax, 14, 23, 11.5, 21, '', 'dashed', 1.5)
draw_arrow(ax, 14, 23, 17.5, 21, '', 'dashed', 1.5)
draw_arrow(ax, 14, 23, 5.5, 17.5, '', 'dashed', 1.5)
draw_arrow(ax, 14, 23, 11.5, 17.5, '', 'dashed', 1.5)
draw_arrow(ax, 14, 23, 17.5, 17.5, '', 'dashed', 1.5)

# Arrow from Predictor to ML Engine
draw_arrow(ax, 14, 19.5, 21, 18, 'Inference', 'solid', 2)

# ============================================================================
# TIER 3: DATA & SERVICES LAYER
# ============================================================================
draw_zone_box(ax, 1, 1, 26, 9.5, 'TIER 3: DATA & SERVICES LAYER', 'light')

# Firebase Firestore
draw_component_box(ax, 2, 7, 6, 3,
                  'Firebase Firestore',
                  'NoSQL Database',
                  ['User Profiles', 'Assessments', 'Medical History', 'Real-time Sync', 'Scalable'],
                  'solid')

# Firebase Storage
draw_component_box(ax, 9, 7, 6, 3,
                  'Firebase Storage',
                  'File Storage',
                  ['Medical Reports', 'Images/PDFs', 'Secure Upload', 'CDN Distribution'],
                  'solid')

# Treatment Knowledge Base
draw_component_box(ax, 16, 7, 5, 3,
                  'Treatment KB',
                  'Medical Knowledge',
                  ['Allopathy DB', 'Ayurveda DB', 'Homeopathy DB', 'Drug Interactions'],
                  'solid')

# External Services
draw_component_box(ax, 22, 7, 4, 3,
                  'External Services',
                  'Third-Party APIs',
                  ['Gemini AI', 'Firebase Auth', 'Analytics'],
                  'dashed')

# Cache Layer
draw_component_box(ax, 2, 3.5, 6, 2.5,
                  'Cache Layer',
                  'Redis / In-Memory',
                  ['Session Cache', 'API Response Cache', 'ML Model Cache', 'Performance Boost'],
                  'shaded')

# Task Queue
draw_component_box(ax, 9, 3.5, 6, 2.5,
                  'Task Queue',
                  'Celery + Redis',
                  ['Async Processing', 'Report Extraction', 'Email Notifications', 'Scheduled Tasks'],
                  'shaded')

# Monitoring & Logging
draw_component_box(ax, 16, 3.5, 5, 2.5,
                  'Monitoring',
                  'Observability',
                  ['Application Logs', 'Error Tracking', 'Performance Metrics', 'Health Checks'],
                  'shaded')

# Security Layer
draw_component_box(ax, 22, 3.5, 4, 2.5,
                  'Security',
                  'Protection Layer',
                  ['Encryption', 'Firewall', 'DDoS Protection', 'HIPAA Ready'],
                  'shaded')

# Arrows from Application to Data Layer
draw_arrow(ax, 5, 12.5, 5, 10, 'Store/Retrieve', 'solid', 2)
draw_arrow(ax, 11.5, 12.5, 12, 10, 'Upload/Download', 'solid', 2)
draw_arrow(ax, 17.5, 12.5, 18.5, 10, 'Query', 'solid', 2)
draw_arrow(ax, 14, 12.5, 24, 10, 'API Calls', 'dashed', 1.5)

# ============================================================================
# SECURITY PERIMETER
# ============================================================================
# Security border
security_border = Rectangle((0.5, 0.5), 27, 35,
                           facecolor='none',
                           edgecolor=COLORS['black'],
                           linewidth=4,
                           linestyle=':')
ax.add_patch(security_border)

# Security badges
security_badges = [
    (2, 0.8, 'HTTPS/TLS 1.3'),
    (7, 0.8, 'OAuth 2.0'),
    (12, 0.8, 'JWT Tokens'),
    (17, 0.8, 'Rate Limiting'),
    (22, 0.8, 'HIPAA Ready')
]

for x, y, label in security_badges:
    badge_box = Rectangle((x - 1, y - 0.3), 2, 0.6,
                         facecolor=COLORS['dark_gray'],
                         edgecolor=COLORS['black'],
                         linewidth=1.5)
    ax.add_patch(badge_box)
    ax.text(x, y, label,
           ha='center', va='center', fontsize=7,
           fontweight='bold', color=COLORS['white'])

# ============================================================================
# LEGEND
# ============================================================================
legend_y = 1.8
ax.text(14, legend_y + 0.8, 'LEGEND',
       ha='center', va='center', fontsize=11,
       fontweight='bold', color=COLORS['black'])

# Legend items
legend_items = [
    ('Solid Line', 'solid', 'Synchronous Call'),
    ('Dashed Line', 'dashed', 'Asynchronous Call'),
    ('White Box', 'white', 'Core Component'),
    ('Gray Box', 'gray', 'Support Service')
]

legend_x = 3
for label, style, desc in legend_items:
    if style == 'solid':
        ax.plot([legend_x, legend_x + 1], [legend_y, legend_y],
               'k-', linewidth=2)
    elif style == 'dashed':
        ax.plot([legend_x, legend_x + 1], [legend_y, legend_y],
               'k--', linewidth=2)
    elif style == 'white':
        box = Rectangle((legend_x, legend_y - 0.2), 1, 0.4,
                       facecolor=COLORS['white'],
                       edgecolor=COLORS['black'],
                       linewidth=1.5)
        ax.add_patch(box)
    else:
        box = Rectangle((legend_x, legend_y - 0.2), 1, 0.4,
                       facecolor=COLORS['very_light_gray'],
                       edgecolor=COLORS['black'],
                       linewidth=1.5)
        ax.add_patch(box)
    
    ax.text(legend_x + 1.5, legend_y, desc,
           ha='left', va='center', fontsize=8,
           color=COLORS['black'])
    legend_x += 6

# ============================================================================
# FOOTER
# ============================================================================
footer_bg = Rectangle((1, 0.2), 26, 0.5,
                      facecolor=COLORS['very_light_gray'],
                      edgecolor=COLORS['black'],
                      linewidth=2)
ax.add_patch(footer_bg)

ax.text(3, 0.45, '© 2024 SymptomSense Health AI',
       ha='left', va='center', fontsize=9,
       color=COLORS['black'])

ax.text(14, 0.45, 'System Architecture - Black & White Edition',
       ha='center', va='center', fontsize=9,
       fontweight='bold', color=COLORS['black'])

ax.text(25, 0.45, 'Confidential',
       ha='right', va='center', fontsize=9,
       color=COLORS['black'])

# ============================================================================
# SAVE
# ============================================================================
script_dir = os.path.dirname(os.path.abspath(__file__))

plt.tight_layout()

# Save PNG versions
png_path = os.path.join(script_dir, 'SymptomSense_Architecture_BW.png')
plt.savefig(png_path,
            dpi=300, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"✓ Black & White architecture diagram saved: {png_path}")

highres_path = os.path.join(script_dir, 'SymptomSense_Architecture_BW_HighRes.png')
plt.savefig(highres_path,
            dpi=600, bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"✓ High-res B&W architecture diagram saved: {highres_path}")

pdf_path = os.path.join(script_dir, 'SymptomSense_Architecture_BW.pdf')
plt.savefig(pdf_path,
            bbox_inches='tight', facecolor='white', edgecolor='none')
print(f"✓ PDF B&W architecture diagram saved: {pdf_path}")

plt.close()

print("\n" + "="*70)
print("BLACK & WHITE ARCHITECTURE DIAGRAM GENERATION COMPLETE!")
print("="*70)
print("\nGenerated files:")
print("1. SymptomSense_Architecture_BW.png (300 DPI)")
print("2. SymptomSense_Architecture_BW_HighRes.png (600 DPI)")
print("3. SymptomSense_Architecture_BW.pdf (Vector)")
print("\nFeatures:")
print("• Professional black & white design")
print("• Optimized for printing and photocopying")
print("• Clear grayscale differentiation")
print("• Three-tier architecture visualization")
print("• Multi-agent system with 6 agents")
print("• Security perimeter overlay")
print("• Perfect for documentation and reports")
print("• Cost-effective printing")
