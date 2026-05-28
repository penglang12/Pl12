# Design Audit Checklist

Detailed criteria for each audit dimension. Use this during Step 1 of the audit protocol.

## Visual Hierarchy

- Does the eye land where it should?
- Is the most important element the most prominent?
- Can a user understand the screen in 2 seconds?
- Every screen has one primary action—is it unmissable?
- Secondary actions support, they never compete
- If everything is bold, nothing is bold
- Visual weight must match functional importance

## Spacing & Rhythm

- Is whitespace consistent and intentional?
- Do elements breathe or are they cramped?
- Is the vertical rhythm harmonious?
- Crowded interfaces feel cheap; breathing room feels premium
- When in doubt, add more space, not more elements

## Typography

- Are type sizes establishing clear hierarchy?
- Are there too many font weights or sizes competing?
- Does the type feel calm or chaotic?
- Type scale should follow consistent ratios
- Line heights appropriate for each size
- Letter spacing considered for headings

## Color

- Is color used with restraint and purpose?
- Do colors guide attention or scatter it?
- Is contrast sufficient for accessibility (WCAG AA minimum)?
- Primary color reserved for primary actions
- Semantic colors (error, success, warning) used consistently
- No more than 2-3 primary colors plus neutrals

## Alignment & Grid

- Do elements sit on a consistent grid?
- Is anything off by 1-2 pixels?
- Does every element feel locked into the layout with precision?
- The eye detects misalignment before the brain can name it
- Check: buttons, text blocks, images, cards all align

## Components

- Are similar elements styled identically across screens?
- Are interactive elements obviously interactive?
- Are disabled states, hover states, and focus states all accounted for?
- Buttons consistent in padding, border-radius, font weight
- Form inputs share consistent height, padding, border treatment
- Cards share shadow depth, border radius, padding

## Iconography

- Are icons consistent in style, weight, and size across the entire app?
- Are they from one cohesive set or mixed from different libraries?
- Do they support meaning or just decorate?
- Icon stroke weights should match (1.5px, 2px, etc.)
- Icon sizes should follow a scale (16, 20, 24px)
- Fill vs outline used consistently for state

## Motion & Transitions

- Do transitions feel natural and purposeful?
- Is there motion that exists for no reason?
- Does the app feel responsive to touch/click?
- Are animations possible within the current tech stack?
- Timing: 150-300ms for micro-interactions, 300-500ms for page transitions
- Easing: ease-out for entrances, ease-in for exits

## Empty States

- What does every screen look like with no data?
- Do blank screens feel intentional or broken?
- Is the user guided toward their first action?
- Empty states should have: illustration/icon, heading, description, CTA
- Tone should be helpful, not apologetic

## Loading States

- Are skeleton screens, spinners, or placeholders consistent?
- Does the app feel alive while waiting or frozen?
- Skeletons preferred over spinners for content areas
- Loading indicators appear after 200ms delay (avoid flash)
- Progress indicators for operations > 3 seconds

## Error States

- Are error messages styled consistently?
- Do they feel helpful and clear or hostile and technical?
- Inline validation preferred over submit-time errors
- Error messages should: say what went wrong, how to fix it
- Red reserved for errors, not decorative use

## Dark Mode / Theming

- If supported, is it actually designed or just inverted?
- Do all tokens, shadows, and contrast ratios hold up across themes?
- Shadows become glows or reduce in dark mode
- Backgrounds use dark grays, not pure black (#121212 not #000)
- Contrast ratios rechecked in dark mode

## Density

- Can anything be removed without losing meaning?
- Are there redundant elements saying the same thing twice?
- Is every element earning its place on screen?
- Labels + placeholders = redundant
- Icon + label when icon is unclear = fine
- Two CTAs doing same thing = remove one

## Responsiveness

- Does every screen work at mobile, tablet, and desktop?
- Are touch targets sized for thumbs on touch devices (44x44px min)?
- Does the layout adapt fluidly across all viewport sizes?
- No screen size should feel like an afterthought
- Test: 375px, 768px, 1024px, 1440px viewports
- Navigation adapts: hamburger on mobile, tabs/sidebar on desktop

## Accessibility

- Keyboard navigation functional for all interactive elements
- Focus states visible and styled
- ARIA labels for non-text interactive elements
- Color contrast ratios meet WCAG AA (4.5:1 text, 3:1 UI)
- Screen reader flow makes semantic sense
- Focus trap in modals
- Skip links for navigation-heavy pages
