import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import Icon from '@/components/ui/icon';
import CreateProject from '@/components/CreateProject';
import AnalyzeCode from '@/components/AnalyzeCode';
import ModifyProject from '@/components/ModifyProject';
import GitHubIntegration from '@/components/GitHubIntegration';
import TestingPanel from '@/components/TestingPanel';
import DocumentationPanel from '@/components/DocumentationPanel';

const Index = () => {
  const [activeTab, setActiveTab] = useState('create');
  const [language, setLanguage] = useState('ru');
  const [aiModel, setAiModel] = useState('gpt4');

  const stats = [
    { label: 'Проектов создано', value: '127', icon: 'FolderGit2', color: 'text-primary' },
    { label: 'Строк кода', value: '45.2K', icon: 'Code2', color: 'text-secondary' },
    { label: 'Ошибок исправлено', value: '89', icon: 'Bug', color: 'text-green-500' },
    { label: 'Время экономии', value: '156ч', icon: 'Clock', color: 'text-orange-500' },
  ];

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border/40 bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
                <Icon name="Sparkles" className="text-white" size={20} />
              </div>
              <div>
                <h1 className="text-xl font-semibold">AI Developer Agent</h1>
                <p className="text-xs text-muted-foreground">Интеллектуальный помощник программиста</p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <Select value={language} onValueChange={setLanguage}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ru">🇷🇺 Русский</SelectItem>
                  <SelectItem value="en">🇬🇧 English</SelectItem>
                  <SelectItem value="zh">🇨🇳 中文</SelectItem>
                  <SelectItem value="es">🇪🇸 Español</SelectItem>
                </SelectContent>
              </Select>

              <Select value={aiModel} onValueChange={setAiModel}>
                <SelectTrigger className="w-40">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt4">GPT-4 Turbo</SelectItem>
                  <SelectItem value="gpt3">GPT-3.5</SelectItem>
                  <SelectItem value="claude">Claude 3</SelectItem>
                  <SelectItem value="gemini">Gemini Pro</SelectItem>
                  <SelectItem value="mixtral">Mixtral 8x7B</SelectItem>
                </SelectContent>
              </Select>

              <Button variant="outline" size="icon">
                <Icon name="Settings" size={18} />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8 animate-fade-in">
          {stats.map((stat, index) => (
            <Card key={index} className="hover-scale cursor-pointer">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground mb-1">{stat.label}</p>
                    <p className="text-3xl font-bold">{stat.value}</p>
                  </div>
                  <div className={`w-12 h-12 rounded-xl bg-muted flex items-center justify-center ${stat.color}`}>
                    <Icon name={stat.icon} size={24} />
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="animate-scale-in">
          <TabsList className="grid w-full grid-cols-6 mb-8">
            <TabsTrigger value="create" className="flex items-center gap-2">
              <Icon name="Plus" size={16} />
              Создание
            </TabsTrigger>
            <TabsTrigger value="analyze" className="flex items-center gap-2">
              <Icon name="Search" size={16} />
              Анализ
            </TabsTrigger>
            <TabsTrigger value="modify" className="flex items-center gap-2">
              <Icon name="Wrench" size={16} />
              Модификация
            </TabsTrigger>
            <TabsTrigger value="github" className="flex items-center gap-2">
              <Icon name="Github" size={16} />
              GitHub
            </TabsTrigger>
            <TabsTrigger value="test" className="flex items-center gap-2">
              <Icon name="CheckCircle" size={16} />
              Тестирование
            </TabsTrigger>
            <TabsTrigger value="docs" className="flex items-center gap-2">
              <Icon name="FileText" size={16} />
              Документация
            </TabsTrigger>
          </TabsList>

          <TabsContent value="create" className="animate-fade-in">
            <CreateProject aiModel={aiModel} language={language} />
          </TabsContent>

          <TabsContent value="analyze" className="animate-fade-in">
            <AnalyzeCode aiModel={aiModel} language={language} />
          </TabsContent>

          <TabsContent value="modify" className="animate-fade-in">
            <ModifyProject aiModel={aiModel} language={language} />
          </TabsContent>

          <TabsContent value="github" className="animate-fade-in">
            <GitHubIntegration language={language} />
          </TabsContent>

          <TabsContent value="test" className="animate-fade-in">
            <TestingPanel aiModel={aiModel} language={language} />
          </TabsContent>

          <TabsContent value="docs" className="animate-fade-in">
            <DocumentationPanel aiModel={aiModel} language={language} />
          </TabsContent>
        </Tabs>
      </main>

      <footer className="border-t border-border/40 mt-16">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <p>© 2026 AI Developer Agent. Автоматизация разработки ПО.</p>
            <div className="flex items-center gap-4">
              <Badge variant="outline" className="gap-1">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                Система активна
              </Badge>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
