#!/bin/bash
# Script to deploy enhanced admin dashboard on render.com

echo "=================================================="
echo "Deploying Enhanced Admin Dashboard on render.com"
echo "=================================================="

# Make sure scripts are executable
chmod +x enhanced_admin_dashboard.py
chmod +x activate_enhanced_dashboard.py
chmod +x direct_admin_dashboard_patch.py

# Apply the direct patch
echo "Applying direct patch to admin.py..."
python direct_admin_dashboard_patch.py

# Create .render-buildsteps.json to run on deployment
cat > .render-buildsteps.json << 'EOF'
{
  "buildSteps": [
    {
      "name": "Apply Enhanced Admin Dashboard",
      "command": "python direct_admin_dashboard_patch.py",
      "onBoot": true
    }
  ]
}
EOF

echo "Created .render-buildsteps.json for automatic deployment"
echo ""
echo "✅ Enhanced Admin Dashboard is now configured for render.com"
echo "When your application starts, the admin dashboard will be automatically enhanced."
echo ""
echo "Access the enhanced dashboard at: /admin/dashboard"