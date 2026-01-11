import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Icon from '@/components/ui/icon';

interface AnalyzeCodeProps {
  aiModel: string;
  language: string;
}

const AnalyzeCode = ({ aiModel, language }: AnalyzeCodeProps) => {
  const [repoUrl, setRepoUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const metrics = [
    { label: 'Качество кода', value: 87, color: 'bg-green-500', icon: 'Award' },
    { label: 'Производительность', value: 72, color: 'bg-blue-500', icon: 'Zap' },
    { label: 'Безопасность', value: 91, color: 'bg-purple-500', icon: 'Shield' },
    { label: 'Читаемость', value: 78, color: 'bg-orange-500', icon: 'Eye' },
  ];

  const issues = [
    { type: 'error', count: 3, label: 'Критические ошибки', color: 'text-red-500' },
    { type: 'warning', count: 12, label: 'Предупреждения', color: 'text-yellow-500' },
    { type: 'info', count: 8, label: 'Рекомендации', color: 'text-blue-500' },
  ];

  const codeSmells = [
    { file: 'src/utils/api.ts', line: 47, issue: 'Дублирование кода', severity: 'medium' },
    { file: 'src/components/User.tsx', line: 123, issue: 'Сложная функция (15 строк)', severity: 'low' },
    { file: 'src/services/auth.ts', line: 89, issue: 'Отсутствует обработка ошибок', severity: 'high' },
    { file: 'src/hooks/useData.ts', line: 34, issue: 'Неиспользуемая переменная', severity: 'low' },
  ];

  const handleAnalyze = () => {
    setIsAnalyzing(true);
    setTimeout(() => setIsAnalyzing(false), 2500);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Icon name="Search" size={20} />
              Анализ кода
            </CardTitle>
            <CardDescription>
              Загрузите проект из GitHub или локальной папки для глубокого анализа
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label>URL репозитория или путь к проекту</Label>
              <div className="flex gap-2 mt-2">
                <Input
                  placeholder="https://github.com/username/project или /path/to/project"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                />
                <Button variant="outline" size="icon">
                  <Icon name="FolderOpen" size={18} />
                </Button>
              </div>
            </div>

            <Button
              className="w-full"
              size="lg"
              onClick={handleAnalyze}
              disabled={isAnalyzing || !repoUrl}
            >
              {isAnalyzing ? (
                <>
                  <Icon name="Loader2" className="animate-spin mr-2" size={18} />
                  Анализ...
                </>
              ) : (
                <>
                  <Icon name="Play" className="mr-2" size={18} />
                  Запустить анализ
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Метрики качества</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {metrics.map((metric, idx) => (
              <div key={idx}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon name={metric.icon} size={16} className={metric.color.replace('bg-', 'text-')} />
                    <span className="text-sm font-medium">{metric.label}</span>
                  </div>
                  <span className="text-sm font-bold">{metric.value}%</span>
                </div>
                <Progress value={metric.value} className="h-2" />
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Найденные проблемы</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="all">
              <TabsList className="w-full">
                <TabsTrigger value="all" className="flex-1">Все</TabsTrigger>
                <TabsTrigger value="errors" className="flex-1">Ошибки</TabsTrigger>
                <TabsTrigger value="warnings" className="flex-1">Предупреждения</TabsTrigger>
              </TabsList>
              <TabsContent value="all" className="space-y-2 mt-4">
                {codeSmells.map((smell, idx) => (
                  <Card key={idx} className="hover:bg-accent transition-colors cursor-pointer">
                    <CardContent className="pt-3 pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <code className="text-xs bg-muted px-2 py-0.5 rounded">{smell.file}</code>
                            <Badge variant="outline" className="text-xs">Строка {smell.line}</Badge>
                          </div>
                          <p className="text-sm">{smell.issue}</p>
                        </div>
                        <Badge
                          variant={smell.severity === 'high' ? 'destructive' : 'outline'}
                          className={smell.severity === 'medium' ? 'bg-yellow-500 text-white' : ''}
                        >
                          {smell.severity === 'high' && 'Высокий'}
                          {smell.severity === 'medium' && 'Средний'}
                          {smell.severity === 'low' && 'Низкий'}
                        </Badge>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="BarChart3" size={18} />
              Статистика
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Файлов</span>
              <span className="font-bold">247</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Строк кода</span>
              <span className="font-bold">18,432</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Комментариев</span>
              <span className="font-bold">1,245</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-muted-foreground">Тестов</span>
              <span className="font-bold">86</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="AlertCircle" size={18} />
              Сводка проблем
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {issues.map((issue, idx) => (
              <div key={idx} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Icon name="Circle" size={8} className={issue.color} />
                  <span className="text-sm">{issue.label}</span>
                </div>
                <Badge variant="outline">{issue.count}</Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="TrendingUp" size={18} />
              Рекомендации
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="flex items-start gap-2">
              <Icon name="ArrowRight" className="text-primary mt-0.5" size={16} />
              <span>Добавить unit-тесты для критических модулей</span>
            </div>
            <div className="flex items-start gap-2">
              <Icon name="ArrowRight" className="text-primary mt-0.5" size={16} />
              <span>Рефакторинг функций длиннее 50 строк</span>
            </div>
            <div className="flex items-start gap-2">
              <Icon name="ArrowRight" className="text-primary mt-0.5" size={16} />
              <span>Настроить ESLint правила</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default AnalyzeCode;
