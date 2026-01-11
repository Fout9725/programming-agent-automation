import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import Icon from '@/components/ui/icon';

interface TestingPanelProps {
  aiModel: string;
  language: string;
}

const TestingPanel = ({ aiModel, language }: TestingPanelProps) => {
  const testSuites = [
    { name: 'Unit Tests', total: 142, passed: 138, failed: 4, coverage: 87 },
    { name: 'Integration Tests', total: 56, passed: 53, failed: 3, coverage: 72 },
    { name: 'E2E Tests', total: 23, passed: 21, failed: 2, coverage: 65 },
  ];

  const recentTests = [
    { name: 'Auth.test.ts', status: 'passed', duration: '1.2s', coverage: 94 },
    { name: 'API.test.ts', status: 'failed', duration: '0.8s', coverage: 78 },
    { name: 'Utils.test.ts', status: 'passed', duration: '0.3s', coverage: 100 },
    { name: 'Components.test.tsx', status: 'passed', duration: '2.1s', coverage: 85 },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Icon name="CheckCircle" size={20} />
              Автоматическое тестирование
            </CardTitle>
            <CardDescription>
              Агент создает и запускает тесты для вашего кода
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-4">
              <Button className="h-24 flex flex-col items-center justify-center">
                <Icon name="Play" size={24} className="mb-2" />
                <span>Запустить все</span>
              </Button>
              <Button variant="outline" className="h-24 flex flex-col items-center justify-center">
                <Icon name="Plus" size={24} className="mb-2" />
                <span>Создать тесты</span>
              </Button>
              <Button variant="outline" className="h-24 flex flex-col items-center justify-center">
                <Icon name="FileCode" size={24} className="mb-2" />
                <span>Coverage отчет</span>
              </Button>
            </div>

            {testSuites.map((suite, idx) => (
              <Card key={idx}>
                <CardContent className="pt-4 pb-4">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <Icon name="TestTube" className="text-primary" size={20} />
                      <div>
                        <p className="font-medium">{suite.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {suite.passed}/{suite.total} тестов пройдено
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="bg-green-500/10 text-green-500">
                        {suite.passed} ✓
                      </Badge>
                      {suite.failed > 0 && (
                        <Badge variant="outline" className="bg-red-500/10 text-red-500">
                          {suite.failed} ✗
                        </Badge>
                      )}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">Покрытие кода</span>
                      <span className="font-medium">{suite.coverage}%</span>
                    </div>
                    <Progress value={suite.coverage} className="h-2" />
                  </div>
                </CardContent>
              </Card>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="Clock" size={18} />
              Последние запуски
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {recentTests.map((test, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-muted rounded-lg hover:bg-accent transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <Icon
                    name={test.status === 'passed' ? 'CheckCircle2' : 'XCircle'}
                    className={test.status === 'passed' ? 'text-green-500' : 'text-red-500'}
                    size={18}
                  />
                  <div>
                    <code className="text-sm font-medium">{test.name}</code>
                    <p className="text-xs text-muted-foreground">
                      {test.duration} • {test.coverage}% покрытие
                    </p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  <Icon name="Play" size={14} />
                </Button>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="BarChart3" size={18} />
              Общая статистика
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm">Общее покрытие</span>
                <span className="font-bold text-lg">82%</span>
              </div>
              <Progress value={82} className="h-3" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="text-center p-3 bg-green-500/10 rounded-lg">
                <p className="text-2xl font-bold text-green-500">212</p>
                <p className="text-xs text-muted-foreground">Пройдено</p>
              </div>
              <div className="text-center p-3 bg-red-500/10 rounded-lg">
                <p className="text-2xl font-bold text-red-500">9</p>
                <p className="text-xs text-muted-foreground">Провалено</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="Zap" size={18} />
              AI Автотесты
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="text-muted-foreground">
              Агент автоматически создает тесты при добавлении нового кода
            </p>
            <div className="flex items-start gap-2">
              <Icon name="Check" className="text-green-500 mt-0.5" size={16} />
              <span>Unit тесты для функций</span>
            </div>
            <div className="flex items-start gap-2">
              <Icon name="Check" className="text-green-500 mt-0.5" size={16} />
              <span>Интеграционные тесты</span>
            </div>
            <div className="flex items-start gap-2">
              <Icon name="Check" className="text-green-500 mt-0.5" size={16} />
              <span>Тесты на регрессию</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="Bug" size={18} />
              Найденные баги
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Критические</span>
                <Badge variant="destructive">2</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Важные</span>
                <Badge variant="outline" className="bg-yellow-500/10 text-yellow-600">5</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Минорные</span>
                <Badge variant="outline">12</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default TestingPanel;
