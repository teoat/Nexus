/**
 * 📏 Spacing Design Tokens
 * Comprehensive spacing system for Nexus Platform
 */

export const spacing = {
  // Base spacing unit (4px)
  base: 4,

  // Spacing scale (4px increments)
  scale: {
    0: '0px',
    0.5: '2px',   // 0.5 * 4px
    1: '4px',     // 1 * 4px
    1.5: '6px',   // 1.5 * 4px
    2: '8px',     // 2 * 4px
    2.5: '10px',  // 2.5 * 4px
    3: '12px',    // 3 * 4px
    3.5: '14px',  // 3.5 * 4px
    4: '16px',    // 4 * 4px
    5: '20px',    // 5 * 4px
    6: '24px',    // 6 * 4px
    7: '28px',    // 7 * 4px
    8: '32px',    // 8 * 4px
    9: '36px',    // 9 * 4px
    10: '40px',   // 10 * 4px
    11: '44px',   // 11 * 4px
    12: '48px',   // 12 * 4px
    14: '56px',   // 14 * 4px
    16: '64px',   // 16 * 4px
    20: '80px',   // 20 * 4px
    24: '96px',   // 24 * 4px
    28: '112px',  // 28 * 4px
    32: '128px',  // 32 * 4px
    36: '144px',  // 36 * 4px
    40: '160px',  // 40 * 4px
    44: '176px',  // 44 * 4px
    48: '192px',  // 48 * 4px
    52: '208px',  // 52 * 4px
    56: '224px',  // 56 * 4px
    60: '240px',  // 60 * 4px
    64: '256px',  // 64 * 4px
    72: '288px',  // 72 * 4px
    80: '320px',  // 80 * 4px
    96: '384px',  // 96 * 4px
  },

  // Semantic spacing
  semantic: {
    // Component spacing
    component: {
      xs: '4px',    // Tight spacing
      sm: '8px',    // Small spacing
      md: '16px',   // Medium spacing
      lg: '24px',   // Large spacing
      xl: '32px',   // Extra large spacing
      '2xl': '48px', // 2x extra large spacing
    },

    // Layout spacing
    layout: {
      xs: '8px',    // Tight layout
      sm: '16px',   // Small layout
      md: '24px',   // Medium layout
      lg: '32px',   // Large layout
      xl: '48px',   // Extra large layout
      '2xl': '64px', // 2x extra large layout
    },

    // Section spacing
    section: {
      xs: '32px',   // Tight section
      sm: '48px',   // Small section
      md: '64px',   // Medium section
      lg: '80px',   // Large section
      xl: '96px',   // Extra large section
      '2xl': '128px', // 2x extra large section
    },

    // Container spacing
    container: {
      xs: '16px',   // Tight container
      sm: '24px',   // Small container
      md: '32px',   // Medium container
      lg: '48px',   // Large container
      xl: '64px',   // Extra large container
      '2xl': '80px', // 2x extra large container
    },
  },

  // Responsive spacing
  responsive: {
    mobile: {
      component: {
        xs: '4px',
        sm: '8px',
        md: '12px',
        lg: '16px',
        xl: '20px',
        '2xl': '24px',
      },
      layout: {
        xs: '8px',
        sm: '12px',
        md: '16px',
        lg: '20px',
        xl: '24px',
        '2xl': '32px',
      },
      section: {
        xs: '16px',
        sm: '24px',
        md: '32px',
        lg: '40px',
        xl: '48px',
        '2xl': '64px',
      },
    },
    tablet: {
      component: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '20px',
        xl: '24px',
        '2xl': '32px',
      },
      layout: {
        xs: '8px',
        sm: '16px',
        md: '20px',
        lg: '24px',
        xl: '32px',
        '2xl': '40px',
      },
      section: {
        xs: '24px',
        sm: '32px',
        md: '40px',
        lg: '48px',
        xl: '64px',
        '2xl': '80px',
      },
    },
    desktop: {
      component: {
        xs: '4px',
        sm: '8px',
        md: '16px',
        lg: '24px',
        xl: '32px',
        '2xl': '48px',
      },
      layout: {
        xs: '8px',
        sm: '16px',
        md: '24px',
        lg: '32px',
        xl: '48px',
        '2xl': '64px',
      },
      section: {
        xs: '32px',
        sm: '48px',
        md: '64px',
        lg: '80px',
        xl: '96px',
        '2xl': '128px',
      },
    },
  },

  // Grid spacing
  grid: {
    columns: 12,
    gutter: '24px',
    margin: '0 auto',
    maxWidth: '1200px',
    breakpoints: {
      sm: '640px',
      md: '768px',
      lg: '1024px',
      xl: '1280px',
      '2xl': '1536px',
    },
  },

  // Border radius
  borderRadius: {
    none: '0px',
    sm: '4px',
    md: '8px',
    lg: '12px',
    xl: '16px',
    '2xl': '20px',
    '3xl': '24px',
    full: '9999px',
  },

  // Shadows (spacing-related)
  shadow: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    inner: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
    none: 'none',
  },

  // Z-index scale
  zIndex: {
    hide: -1,
    auto: 'auto',
    base: 0,
    docked: 10,
    dropdown: 1000,
    sticky: 1100,
    banner: 1200,
    overlay: 1300,
    modal: 1400,
    popover: 1500,
    skipLink: 1600,
    toast: 1700,
    tooltip: 1800,
  },
} as const;

// Spacing utility functions
export const getSpacing = (size: keyof typeof spacing.scale) => spacing.scale[size];
export const getSemanticSpacing = (category: keyof typeof spacing.semantic, size: keyof typeof spacing.semantic.component) => 
  spacing.semantic[category][size];

// Responsive spacing utilities
export const getResponsiveSpacing = (
  category: keyof typeof spacing.semantic,
  size: keyof typeof spacing.semantic.component,
  breakpoint: 'mobile' | 'tablet' | 'desktop' = 'desktop'
) => {
  const responsiveSpacing = spacing.responsive[breakpoint][category][size as keyof typeof spacing.responsive.mobile.component];
  return responsiveSpacing || spacing.semantic[category][size];
};

// Grid utilities
export const getGridGutter = () => spacing.grid.gutter;
export const getGridMaxWidth = () => spacing.grid.maxWidth;
export const getGridBreakpoint = (breakpoint: keyof typeof spacing.grid.breakpoints) => 
  spacing.grid.breakpoints[breakpoint];

// Shadow utilities
export const getShadow = (size: keyof typeof spacing.shadow) => spacing.shadow[size];

// Z-index utilities
export const getZIndex = (level: keyof typeof spacing.zIndex) => spacing.zIndex[level];

// Spacing calculation utilities
export const calculateSpacing = (multiplier: number) => `${spacing.base * multiplier}px`;
export const calculateResponsiveSpacing = (multiplier: number, breakpoint: 'mobile' | 'tablet' | 'desktop') => {
  const responsiveMultiplier = breakpoint === 'mobile' ? multiplier * 0.75 : 
                              breakpoint === 'tablet' ? multiplier * 0.875 : multiplier;
  return `${spacing.base * responsiveMultiplier}px`;
};

// Layout utilities
export const getContainerPadding = (breakpoint: 'mobile' | 'tablet' | 'desktop' = 'desktop') => {
  const padding = breakpoint === 'mobile' ? '16px' : 
                  breakpoint === 'tablet' ? '24px' : '32px';
  return padding;
};

export const getSectionSpacing = (breakpoint: 'mobile' | 'tablet' | 'desktop' = 'desktop') => {
  const sectionSpacing = breakpoint === 'mobile' ? '32px' : 
                        breakpoint === 'tablet' ? '48px' : '64px';
  return sectionSpacing;
};

export type SpacingSize = keyof typeof spacing.scale;
export type SemanticSpacingCategory = keyof typeof spacing.semantic;
export type ResponsiveBreakpoint = keyof typeof spacing.responsive;
export type ShadowSize = keyof typeof spacing.shadow;
export type ZIndexLevel = keyof typeof spacing.zIndex;
