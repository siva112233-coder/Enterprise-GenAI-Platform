/**
 * App — root React component.
 *
 * Mounts the RouterProvider with the application router.
 * This is the only file that knows about the router — all other
 * components use React Router hooks to access routing state.
 */

import { RouterProvider } from 'react-router-dom'
import { router } from '@/router'

export default function App() {
  return <RouterProvider router={router} />
}
