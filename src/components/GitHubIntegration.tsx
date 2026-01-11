import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import Icon from '@/components/ui/icon';

interface GitHubIntegrationProps {
  language: string;
}

const GitHubIntegration = ({ language }: GitHubIntegrationProps) => {
  const repos = [
    { name: 'ai-chatbot', branch: 'main', commits: 47, status: 'synced', lastSync: '5 мин назад' },
    { name: 'ecommerce-app', branch: 'develop', commits: 123, status: 'pending', lastSync: '2 часа назад' },
    { name: 'mobile-game', branch: 'main', commits: 89, status: 'synced', lastSync: '1 час назад' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Icon name="Github" size={20} />
              GitHub Интеграция
            </CardTitle>
            <CardDescription>
              Подключите GitHub для автоматической синхронизации кода
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                  <Icon name="Github" size={20} className="text-primary" />
                </div>
                <div>
                  <p className="font-medium">Аккаунт подключен</p>
                  <p className="text-sm text-muted-foreground">@username</p>
                </div>
              </div>
              <Button variant="outline">Отключить</Button>
            </div>

            <div>
              <Label>Новый репозиторий</Label>
              <div className="flex gap-2 mt-2">
                <Input placeholder="Название репозитория" />
                <Button>
                  <Icon name="Plus" className="mr-2" size={16} />
                  Создать
                </Button>
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <Label>Автосинхронизация</Label>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <Label>Создавать PR для изменений</Label>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <Label>Защита основной ветки</Label>
                <Switch />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="FolderGit2" size={18} />
              Синхронизированные репозитории
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {repos.map((repo, idx) => (
              <Card key={idx} className="hover:bg-accent transition-colors">
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <Icon name="FolderGit" className="text-primary" size={20} />
                      <div>
                        <p className="font-medium">{repo.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {repo.branch} • {repo.commits} коммитов
                        </p>
                      </div>
                    </div>
                    <Badge variant={repo.status === 'synced' ? 'default' : 'outline'}>
                      {repo.status === 'synced' ? 'Синхронизирован' : 'Ожидает'}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Последняя синхронизация: {repo.lastSync}</span>
                    <div className="flex gap-2">
                      <Button variant="ghost" size="sm">
                        <Icon name="RefreshCw" size={14} />
                      </Button>
                      <Button variant="ghost" size="sm">
                        <Icon name="ExternalLink" size={14} />
                      </Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="GitPullRequest" size={18} />
              Pull Requests
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-2">
                <Icon name="GitPullRequest" className="text-green-500" size={16} />
                <div>
                  <p className="text-sm font-medium">Открытые</p>
                  <p className="text-xs text-muted-foreground">3 PR</p>
                </div>
              </div>
            </div>
            <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
              <div className="flex items-center gap-2">
                <Icon name="GitMerge" className="text-purple-500" size={16} />
                <div>
                  <p className="text-sm font-medium">Объединенные</p>
                  <p className="text-xs text-muted-foreground">47 PR</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="Activity" size={18} />
              Активность
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-start gap-2">
              <Icon name="GitCommit" className="text-primary mt-0.5" size={14} />
              <div className="flex-1">
                <p className="font-medium">23 коммита сегодня</p>
                <p className="text-xs text-muted-foreground">+2,347 / -892 строк</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Icon name="GitBranch" className="text-secondary mt-0.5" size={14} />
              <div className="flex-1">
                <p className="font-medium">5 активных веток</p>
                <p className="text-xs text-muted-foreground">main, develop, feature-x...</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="FileCode" size={18} />
              README автогенерация
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-3">
              Агент автоматически создает и обновляет README.md при изменениях
            </p>
            <Button variant="outline" className="w-full" size="sm">
              <Icon name="FileText" className="mr-2" size={16} />
              Обновить README
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default GitHubIntegration;
