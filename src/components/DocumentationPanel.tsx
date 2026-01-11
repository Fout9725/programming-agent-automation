import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Icon from '@/components/ui/icon';

interface DocumentationPanelProps {
  aiModel: string;
  language: string;
}

const DocumentationPanel = ({ aiModel, language }: DocumentationPanelProps) => {
  const docSections = [
    { title: 'Установка', icon: 'Download', status: 'complete', pages: 3 },
    { title: 'API Reference', icon: 'Code', status: 'complete', pages: 12 },
    { title: 'Руководство', icon: 'Book', status: 'in-progress', pages: 8 },
    { title: 'Примеры', icon: 'Lightbulb', status: 'pending', pages: 0 },
  ];

  const recentDocs = [
    { name: 'README.md', updated: '10 мин назад', size: '4.2 KB' },
    { name: 'API.md', updated: '1 час назад', size: '12.5 KB' },
    { name: 'CONTRIBUTING.md', updated: 'Вчера', size: '2.8 KB' },
    { name: 'CHANGELOG.md', updated: '2 дня назад', size: '8.1 KB' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Icon name="FileText" size={20} />
              Автоматическая документация
            </CardTitle>
            <CardDescription>
              Агент генерирует и поддерживает документацию в актуальном состоянии
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <Button className="h-20 flex flex-col items-center justify-center">
                <Icon name="Sparkles" size={20} className="mb-2" />
                <span className="text-sm">Сгенерировать всё</span>
              </Button>
              <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                <Icon name="FileCode" size={20} className="mb-2" />
                <span className="text-sm">JSDoc комментарии</span>
              </Button>
              <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                <Icon name="FileType" size={20} className="mb-2" />
                <span className="text-sm">TypeDoc</span>
              </Button>
            </div>

            <Tabs defaultValue="readme">
              <TabsList className="w-full">
                <TabsTrigger value="readme" className="flex-1">README</TabsTrigger>
                <TabsTrigger value="api" className="flex-1">API Docs</TabsTrigger>
                <TabsTrigger value="guides" className="flex-1">Руководства</TabsTrigger>
              </TabsList>
              
              <TabsContent value="readme" className="mt-4">
                <Card>
                  <CardContent className="pt-4">
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <h3 className="font-semibold">README.md</h3>
                        <Button variant="ghost" size="sm">
                          <Icon name="Edit" size={14} />
                        </Button>
                      </div>
                      <div className="p-4 bg-muted rounded-lg space-y-2 text-sm font-mono">
                        <p className="text-primary"># AI Developer Agent</p>
                        <p className="text-muted-foreground">
                          Интеллектуальный агент для автоматизации разработки...
                        </p>
                        <p className="text-primary">## Установка</p>
                        <p className="text-muted-foreground">npm install ai-dev-agent</p>
                        <p className="text-primary">## Использование</p>
                        <p className="text-muted-foreground">import Agent from 'ai-dev-agent'</p>
                      </div>
                      <Button className="w-full">
                        <Icon name="RefreshCw" className="mr-2" size={16} />
                        Обновить README
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="api" className="mt-4">
                <div className="space-y-3">
                  {docSections.filter(s => s.title === 'API Reference').map((section, idx) => (
                    <Card key={idx}>
                      <CardContent className="pt-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <Icon name={section.icon} size={18} />
                            <span className="font-medium">{section.title}</span>
                          </div>
                          <Badge>{section.pages} страниц</Badge>
                        </div>
                        <Button variant="outline" className="w-full">
                          Просмотреть документацию
                        </Button>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="FolderOpen" size={18} />
              Разделы документации
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {docSections.map((section, idx) => (
              <Card key={idx} className="hover:bg-accent transition-colors cursor-pointer">
                <CardContent className="pt-3 pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center">
                        <Icon name={section.icon} className="text-primary" size={16} />
                      </div>
                      <div>
                        <p className="font-medium text-sm">{section.title}</p>
                        <p className="text-xs text-muted-foreground">{section.pages} страниц</p>
                      </div>
                    </div>
                    <Badge
                      variant={section.status === 'complete' ? 'default' : 'outline'}
                      className={
                        section.status === 'in-progress' ? 'bg-yellow-500/10 text-yellow-600' : ''
                      }
                    >
                      {section.status === 'complete' && 'Готово'}
                      {section.status === 'in-progress' && 'В работе'}
                      {section.status === 'pending' && 'Не начато'}
                    </Badge>
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
              <Icon name="Clock" size={18} />
              Недавние обновления
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {recentDocs.map((doc, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between p-3 bg-muted rounded-lg hover:bg-accent transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-2">
                  <Icon name="FileText" size={16} className="text-primary" />
                  <div>
                    <p className="text-sm font-medium">{doc.name}</p>
                    <p className="text-xs text-muted-foreground">{doc.updated}</p>
                  </div>
                </div>
                <span className="text-xs text-muted-foreground">{doc.size}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="Zap" size={18} />
              Авто-обновление
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <p className="text-muted-foreground">
              Документация автоматически обновляется при изменении кода
            </p>
            <div className="flex items-start gap-2">
              <Icon name="Check" className="text-green-500 mt-0.5" size={16} />
              <span>Синхронизация с кодом</span>
            </div>
            <div className="flex items-start gap-2">
              <Icon name="Check" className="text-green-500 mt-0.5" size={16} />
              <span>Генерация примеров</span>
            </div>
            <div className="flex items-start gap-2">
              <Icon name="Check" className="text-green-500 mt-0.5" size={16} />
              <span>Мультиязычность</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Icon name="Globe" size={18} />
              Экспорт документации
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Icon name="FileText" className="mr-2" size={14} />
              Markdown
            </Button>
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Icon name="Globe" className="mr-2" size={14} />
              HTML сайт
            </Button>
            <Button variant="outline" className="w-full justify-start" size="sm">
              <Icon name="FileType" className="mr-2" size={14} />
              PDF
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default DocumentationPanel;
