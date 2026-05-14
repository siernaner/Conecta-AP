"use client";
import Link from 'next/link';
import { useContext } from 'react';
import { AuthContext } from '../contexts/AuthContext';

export default function NavBar() {
    const { user, signOut } = useContext(AuthContext);

    return (
        <nav className="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
            <div className="container">
                <Link href="/" className="navbar-brand fw-bold">
                    Conecta Alta Paulista
                </Link>
                
                <div className="d-flex align-items-center">
                    {user ? (
                        <div className="d-flex gap-3 align-items-center text-white">
                            <span>Olá, <strong>{user.nome}</strong></span>
                            
                            {user.role === 'admin' && (
                                <Link href="/admin" className="text-info text-decoration-none">
                                    Gerenciar Painel
                                </Link>
                            )}
                            
                            <button onClick={signOut} className="btn btn-sm btn-danger">
                                Sair
                            </button>
                        </div>
                    ) : (
                        <Link href="/login" className="btn btn-primary btn-sm">
                            Entrar / Cadastrar
                        </Link>
                    )}
                </div>
            </div>
        </nav>
    );
}