import 'bootstrap/dist/css/bootstrap.min.css';
import { AuthProvider } from '../contexts/AuthContext';
import NavBar from './NavBar';

export default function RootLayout({ children }) {
  return (
    <html lang="pt-BR">
      <body className="bg-light">
        <AuthProvider>
           <NavBar />
           <main className="container py-4">
              {children}
           </main>
        </AuthProvider>
      </body>
    </html>
  );
}