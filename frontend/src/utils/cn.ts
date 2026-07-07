/**
 * className utility — merges multiple class strings, filtering falsy values.
 *
 * Lightweight alternative to `clsx` for this project scale.
 * Upgrade to `clsx` + `tailwind-merge` if conditional class collisions arise.
 *
 * @example
 * cn('base-class', isActive && 'active', undefined)
 * // => 'base-class active'
 */
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ')
}
