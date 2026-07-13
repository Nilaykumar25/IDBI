# How to Add Team Member Photos

## Step 1: Create the Assets Folder

Create a folder for team photos:
```
c:\Desktop\IDBI\frontend\src\assets\team\
```

You can do this with:
```bash
mkdir c:\Desktop\IDBI\frontend\src\assets\team
```

## Step 2: Add Your Photos

Place your team member photos in the folder:
- `c:\Desktop\IDBI\frontend\src\assets\team\nilay.jpg`
- `c:\Desktop\IDBI\frontend\src\assets\team\riddhima.jpg`

**Recommended photo specs:**
- Format: JPG or PNG
- Dimensions: At least 200x200px (square recommended)
- File size: Under 500KB for web performance
- The CSS will automatically crop to circular shape

## Step 3: Uncomment the Import Statements

In `c:\Desktop\IDBI\frontend\src\pages\Landing.jsx`, find these lines near the top:

```javascript
// Import team photos (add these after you create the assets folder)
// import nilayPhoto from '../assets/team/nilay.jpg'
// import riddhimaPhoto from '../assets/team/riddhima.jpg'
```

Remove the `//` to uncomment them:
```javascript
// Import team photos (add these after you create the assets folder)
import nilayPhoto from '../assets/team/nilay.jpg'
import riddhimaPhoto from '../assets/team/riddhima.jpg'
```

## Step 4: Uncomment the Image Tags

In the same file, find the team section and uncomment the `<img>` tags:

**For Nilay's card:**
```jsx
<div className="member-avatar">
  {/* Uncomment and use image once you add the photo to src/assets/team/ */}
  <img src={nilayPhoto} alt="Nilay Kumar" />
  {/* Remove or comment out the Users icon below */}
  {/* <Users size={40} /> */}
</div>
```

**For Riddhima's card:**
```jsx
<div className="member-avatar">
  {/* Uncomment and use image once you add the photo to src/assets/team/ */}
  <img src={riddhimaPhoto} alt="Riddhima Chaturvedi" />
  {/* Remove or comment out the Users icon below */}
  {/* <Users size={40} /> */}
</div>
```

## Step 5: Test

Save the file and check your browser. The photos should now appear in circular frames!

## Fallback

If you don't have photos yet, the current setup shows a nice icon placeholder (Users icon on a gradient background). The page looks professional either way.

## Photo Tips

- Use professional headshots or casual portraits
- Ensure good lighting and clear facial features
- Square aspect ratio works best
- If photos have different aspect ratios, the CSS will center and crop them automatically
- Test both light and dark mode to ensure photos look good in both themes

## Troubleshooting

**Images not showing?**
1. Check file paths match exactly
2. Check file extensions (.jpg vs .jpeg)
3. Clear browser cache (Ctrl + Shift + R)
4. Check browser console for import errors

**Images look stretched?**
- The CSS `object-fit: cover` should handle this, but ensure photos are at least 200x200px
