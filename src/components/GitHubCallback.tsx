import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent } from '@/components/ui/card';
import Icon from '@/components/ui/icon';

const GitHubCallback = () => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Обработка авторизации...');
  const navigate = useNavigate();

  useEffect(() => {
    const handleCallback = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const code = urlParams.get('code');

      if (!code) {
        setStatus('error');
        setMessage('Не получен код авторизации от GitHub');
        return;
      }

      try {
        const response = await fetch(
          `https://functions.poehali.dev/6cb1e090-32a3-474f-9932-72517de9ce04?action=callback&code=${code}`
        );

        const data = await response.json();

        if (!response.ok || !data.access_token) {
          throw new Error(data.error || 'Не удалось получить токен доступа');
        }

        localStorage.setItem('github_token', data.access_token);
        localStorage.setItem('github_connected', 'true');

        setStatus('success');
        setMessage('GitHub успешно подключен!');

        setTimeout(() => {
          navigate('/?tab=github');
        }, 1500);
      } catch (error) {
        setStatus('error');
        setMessage(error instanceof Error ? error.message : 'Ошибка авторизации');
      }
    };

    handleCallback();
  }, [navigate]);

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-4">
      <Card className="w-full max-w-md">
        <CardContent className="pt-6 text-center">
          {status === 'loading' && (
            <div className="space-y-4">
              <Icon name="Loader2" size={48} className="mx-auto text-primary animate-spin" />
              <p className="text-lg">{message}</p>
            </div>
          )}
          
          {status === 'success' && (
            <div className="space-y-4">
              <Icon name="CheckCircle2" size={48} className="mx-auto text-green-500" />
              <p className="text-lg font-semibold">{message}</p>
              <p className="text-sm text-muted-foreground">Перенаправление...</p>
            </div>
          )}
          
          {status === 'error' && (
            <div className="space-y-4">
              <Icon name="XCircle" size={48} className="mx-auto text-destructive" />
              <p className="text-lg font-semibold">Ошибка</p>
              <p className="text-sm text-muted-foreground">{message}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default GitHubCallback;
