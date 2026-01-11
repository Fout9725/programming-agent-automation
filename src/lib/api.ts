import func2url from '../../backend/func2url.json';

export interface Project {
  id?: number;
  name: string;
  description: string;
  project_type: string;
  technologies?: string[];
  github_url?: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
  versions_count?: number;
}

export interface ProjectVersion {
  id?: number;
  project_id: number;
  version_number?: number;
  change_type: string;
  change_description: string;
  files_changed: string[];
  diff_content?: string;
  ai_model: string;
  created_at?: string;
}

class APIClient {
  private baseUrls = func2url;

  async getAllProjects(): Promise<{ projects: Project[] }> {
    const response = await fetch(this.baseUrls.projects);
    if (!response.ok) throw new Error('Failed to fetch projects');
    return response.json();
  }

  async getProject(id: number): Promise<Project> {
    const response = await fetch(`${this.baseUrls.projects}?id=${id}`);
    if (!response.ok) throw new Error('Failed to fetch project');
    return response.json();
  }

  async createProject(project: Project): Promise<Project> {
    const response = await fetch(this.baseUrls.projects, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(project)
    });
    if (!response.ok) throw new Error('Failed to create project');
    return response.json();
  }

  async updateProject(project: Project): Promise<Project> {
    const response = await fetch(this.baseUrls.projects, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(project)
    });
    if (!response.ok) throw new Error('Failed to update project');
    return response.json();
  }

  async getVersions(projectId: number): Promise<{ versions: ProjectVersion[] }> {
    const response = await fetch(`${this.baseUrls.versions}?project_id=${projectId}`);
    if (!response.ok) throw new Error('Failed to fetch versions');
    return response.json();
  }

  async createVersion(version: ProjectVersion): Promise<ProjectVersion> {
    const response = await fetch(this.baseUrls.versions, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(version)
    });
    if (!response.ok) throw new Error('Failed to create version');
    return response.json();
  }
}

export const api = new APIClient();
