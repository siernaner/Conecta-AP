"use client";
import { useContext, useEffect, useState } from 'react';
import { AuthContext } from '../../contexts/AuthContext';
import { useRouter } from 'next/navigation';

export default function AdminLayout({ children }) {
    const { user, loading } = useContext(AuthContext);
    const router = useRouter();
    const [status, setStatus] = useState('verificando');

    useEffect(() => {
        if (!loading) {
            if (!user || user.role !== 'admin') {
                setStatus('negado');
                setTimeout(() => router.push('/login'), 4000);
            } else {
                setStatus('autorizado');
            }
        }
    }, [user, loading, router]);

    if (loading || status === 'verificando') {
        return (
            <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '50vh' }}>
                <div className="spinner-border text-primary"></div>
            </div>
        );
    }

    if (status === 'negado') {
        return (
            <div className="d-flex flex-column justify-content-center align-items-center text-center" style={{ minHeight: '50vh' }}>
                <i className="bi bi-shield-lock-fill text-danger mb-3" style={{ fontSize: '5rem' }}></i>
                <h2 className="fw-bold text-danger">Você não deveria estar aqui, amiguinho...</h2>
                <p className="text-muted fs-5 mt-2">Redirecionando para a página de login em instantes.</p>
                <div className="spinner-border text-danger mt-3" style={{width: '1.5rem', height: '1.5rem'}}></div>
            </div>
        );
    }

    return <div className="fade-in">{children}</div>;
}