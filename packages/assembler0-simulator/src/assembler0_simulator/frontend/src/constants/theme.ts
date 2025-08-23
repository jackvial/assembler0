// Plain dark theme color constants
export const THEME_COLORS = {
  // Primary Colors
  PRIMARY: '#4A9EFF',           // Soft blue for primary actions
  SUCCESS: '#4ADE80',           // Green for success states
  WARNING: '#FBBF24',           // Yellow for warnings
  ERROR: '#F87171',             // Red for errors
  
  // Background Colors
  BG_PRIMARY: '#0A0A0A',        // Almost black background
  BG_SECONDARY: '#141414',      // Slightly lighter for cards
  BG_ELEVATED: '#1F1F1F',       // Elevated surfaces
  
  // Text Colors
  TEXT_PRIMARY: '#E5E5E5',      // Light gray for primary text
  TEXT_SECONDARY: '#A3A3A3',    // Medium gray for secondary text
  TEXT_MUTED: '#737373',        // Muted gray
  
  // Border Colors
  BORDER: '#262626',            // Dark gray border
  BORDER_LIGHT: '#404040',      // Lighter border for hover states
  
  // Derived Colors with Alpha
  PRIMARY_10: 'rgba(74, 158, 255, 0.1)',
  PRIMARY_20: 'rgba(74, 158, 255, 0.2)',
  PRIMARY_30: 'rgba(74, 158, 255, 0.3)',
  PRIMARY_50: 'rgba(74, 158, 255, 0.5)',
  
  BG_PRIMARY_95: 'rgba(10, 10, 10, 0.95)',
  BG_PRIMARY_90: 'rgba(10, 10, 10, 0.9)',
  BG_PRIMARY_80: 'rgba(10, 10, 10, 0.8)',
  
  BG_SECONDARY_95: 'rgba(20, 20, 20, 0.95)',
  BG_SECONDARY_90: 'rgba(20, 20, 20, 0.9)',
  BG_SECONDARY_80: 'rgba(20, 20, 20, 0.8)',
  
  BORDER_10: 'rgba(38, 38, 38, 0.1)',
  BORDER_20: 'rgba(38, 38, 38, 0.2)',
  BORDER_50: 'rgba(38, 38, 38, 0.5)',
  
  SUCCESS_20: 'rgba(74, 222, 128, 0.2)',
  SUCCESS_40: 'rgba(74, 222, 128, 0.4)',
  ERROR_20: 'rgba(248, 113, 113, 0.2)',
  WARNING_20: 'rgba(251, 191, 36, 0.2)',
  
  // Legacy mappings for compatibility
  METALLIC_RED: '#4A9EFF',
  BEAVER: '#4ADE80',
  DARK_LIVER: '#737373',
  DARK_CHARCOAL: '#141414',
  BULGARIAN_ROSE: '#1F1F1F',
  ROSEWOOD: '#F87171',
  
  DARK_CHARCOAL_95: 'rgba(20, 20, 20, 0.95)',
  DARK_CHARCOAL_90: 'rgba(20, 20, 20, 0.9)',
  DARK_CHARCOAL_80: 'rgba(20, 20, 20, 0.8)',
  DARK_LIVER_95: 'rgba(115, 115, 115, 0.95)',
  DARK_LIVER_50: 'rgba(115, 115, 115, 0.5)',
  DARK_LIVER_33: 'rgba(115, 115, 115, 0.33)',
  DARK_LIVER_20: 'rgba(115, 115, 115, 0.2)',
  DARK_LIVER_10: 'rgba(115, 115, 115, 0.1)',
  METALLIC_RED_33: 'rgba(74, 158, 255, 0.33)',
  METALLIC_RED_66: 'rgba(74, 158, 255, 0.66)',
  METALLIC_RED_50: 'rgba(74, 158, 255, 0.5)',
  METALLIC_RED_40: 'rgba(74, 158, 255, 0.4)',
  METALLIC_RED_20: 'rgba(74, 158, 255, 0.2)',
  METALLIC_RED_10: 'rgba(74, 158, 255, 0.1)',
  METALLIC_RED_03: 'rgba(74, 158, 255, 0.03)',
  BULGARIAN_ROSE_95: 'rgba(31, 31, 31, 0.95)',
  BULGARIAN_ROSE_30: 'rgba(31, 31, 31, 0.3)',
  ROSEWOOD_30: 'rgba(248, 113, 113, 0.3)',
  ROSEWOOD_20: 'rgba(248, 113, 113, 0.2)',
  BEAVER_40: 'rgba(74, 222, 128, 0.4)',
  BEAVER_20: 'rgba(74, 222, 128, 0.2)',
} as const;