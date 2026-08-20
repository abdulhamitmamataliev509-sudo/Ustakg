import '../styles/globals.css'
import Link from 'next/link'

export const metadata = { title: 'Usta kg' }

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <header className="bg-white shadow-sm">
          <div className="container flex items-center justify-between h-16">
            <Link href="/" className="font-bold text-xl">Usta kg</Link>
            <nav className="space-x-4">
              <Link href="/categories">Categories</Link>
              <Link href="/masters">Masters</Link>
              <Link href="/admin">Admin</Link>
            </nav>
          </div>
        </header>
        <main className="container py-8">{children}</main>
      </body>
    </html>
  )
}
