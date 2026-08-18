import { redirect } from 'next/navigation'

export default function Page() {
  // redirect root to public landing
  redirect('/(public)')
}
