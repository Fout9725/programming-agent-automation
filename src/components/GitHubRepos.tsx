import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import Icon from '@/components/ui/icon';

interface Repository {
  name: string;
  full_name: string;
  url: string;
  description: string;
  language: string;
  stars: number;
  updated_at: string;
  default_branch: string;
}

const GitHubRepos = () => {
  const [repos, setRepos] = useState<Repository[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRepos = async () => {
    const token = localStorage.getItem('github_token');
    
    if (!token) {
      setError('Токен GitHub не найден');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(
        'https://functions.poehali.dev/13b30b36-1da4-44b7-ae31-28c5ff1509a8?action=repos',
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          }
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Не удалось загрузить репозитории');
      }

      setRepos(data.repositories);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ошибка загрузки');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = () => {
    localStorage.removeItem('github_token');
    localStorage.removeItem('github_connected');
    window.location.reload();
  };

  useEffect(() => {
    fetchRepos();
  }, []);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins} мин назад`;
    if (diffHours < 24) return `${diffHours} ч назад`;
    return `${diffDays} дн назад`;
  };

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6 text-center">
          <Icon name="Loader2" size={48} className="mx-auto text-primary animate-spin mb-4" />
          <p>Загрузка репозиториев...</p>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="pt-6 text-center">
          <Icon name="XCircle" size={48} className="mx-auto text-destructive mb-4" />
          <p className="text-lg font-semibold mb-2">Ошибка</p>
          <p className="text-sm text-muted-foreground mb-4">{error}</p>
          <Button onClick={() => window.location.reload()}>Повторить</Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Icon name="Github" size={20} />
            GitHub Интеграция
          </CardTitle>
          <CardDescription>
            Подключение активно • {repos.length} репозиториев
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                <Icon name="Github" size={20} className="text-primary" />
              </div>
              <div>
                <p className="font-medium">Аккаунт подключен</p>
                <p className="text-sm text-muted-foreground">GitHub OAuth</p>
              </div>
            </div>
            <Button variant="outline" onClick={handleDisconnect}>Отключить</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="FolderGit2" size={18} />
              Ваши репозитории
            </CardTitle>
            <Button variant="outline" size="sm" onClick={fetchRepos}>
              <Icon name="RefreshCw" size={14} className="mr-2" />
              Обновить
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-3">
          {repos.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <Icon name="FolderOpen" size={48} className="mx-auto mb-2" />
              <p>Репозитории не найдены</p>
            </div>
          ) : (
            repos.map((repo, idx) => (
              <Card key={idx} className="hover:bg-accent transition-colors">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-start gap-3 flex-1">
                      <Icon name="FolderGit" className="text-primary mt-1" size={20} />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-medium">{repo.name}</p>
                          {repo.language && (
                            <Badge variant="outline" className="text-xs">
                              {repo.language}
                            </Badge>
                          )}
                        </div>
                        {repo.description && (
                          <p className="text-sm text-muted-foreground mb-2">
                            {repo.description}
                          </p>
                        )}
                        <div className="flex items-center gap-3 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Icon name="Star" size={12} />
                            {repo.stars}
                          </span>
                          <span className="flex items-center gap-1">
                            <Icon name="GitBranch" size={12} />
                            {repo.default_branch}
                          </span>
                          <span>Обновлен {formatDate(repo.updated_at)}</span>
                        </div>
                      </div>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="sm"
                      onClick={() => window.open(repo.url, '_blank')}
                    >
                      <Icon name="ExternalLink" size={14} />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default GitHubRepos;