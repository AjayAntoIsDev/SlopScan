interface ReadmeAnalysis {
  probability: number;
  reasoning: string;
  summary: string;
  complexity: string;
}

interface CommitAnalysis {
  development_pattern: string;
  time_analysis: any;
  commit_quality: any;
  ai_usage_indicators: any;
  authenticity_score: number;
  slop_indicators: string[];
}

interface CodeFeatures {
  name: string;
  language: string;
  features: {
    language: string;
    function_names: string[];
    classes_names: string[];
    variables_names: string[];
    comments: string[];
  };
}

interface CodeAnalysisResult {
  ai_usage_probability: number;
  code_quality_score: number;
  slop_indicators: string[];
  detailed_analysis: string;
}

interface SomAnalysis {
  authenticity_score: number;
  effort_analysis: any;
  project_analysis: any;
  development_pattern: any;
  slop_indicators: string[];
}

interface SlopScoreResult {
  slopscore: number;
  reasoning: string;
  breakdown: {
    repo_analysis_weight: number;
    code_analysis_weight: number;
    som_analysis_weight: number;
  };
  individual_scores: {
    repo_score: number;
    code_score: number;
    som_score: number;
  };
}

interface AnalysisResult {
  repoAnalysis: {
    aiUsage: number;
    commits: number;
    adequacy: number;
    readmeAnalysis?: ReadmeAnalysis;
    commitAnalysis?: CommitAnalysis;
  };
  somAnalysis: {
    devlogs: number;
    avgTime: string;
    authenticity: number;
    analysis?: SomAnalysis;
  };
  codeAnalysis: {
    aiInCode: number;
    perfectness: number;
    unusedCode: number;
    features?: CodeFeatures[];
    analysis?: CodeAnalysisResult;
  };
  repoSlopScore: number;
  codeSlopScore: number;
  overallSlopScore: number;
  repoInsights: string[];
  codeInsights: string[];
  detailedAnalysis: {
    repo: string;
    code: string;
  };
  slopScoreAnalysis?: SlopScoreResult;
}

interface ProgressCallback {
  (progress: number, status: string): void;
}

class AnalysisService {
  private baseUrl = "http://localhost:8000";

  private isGitHubUrl(url: string): boolean {
    return url.includes("github.com");
  }

  private isSummerOfMakingUrl(url: string): boolean {
    return url.includes("summer.hackclub.com");
  }

  private async getLinksFromSomProject(
    projectUrl: string,
  ): Promise<{ repo_link?: string; readme_link?: string }> {
    try {
      const response = await fetch(
        `${this.baseUrl}/som-analysis/project?project=${encodeURIComponent(projectUrl)}`,
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch project data: ${response.statusText}`);
      }

      const projectData = await response.json();

      return {
        repo_link: projectData.repo_link,
        readme_link: projectData.readme_link,
        som_link: projectUrl,
      };
    } catch (error) {
      console.error("Error fetching Summer of Making project:", error);

      return {};
    }
  }
  async analyzeProject(
    url: string,
    mode: "both" | "repo" | "code",
    onProgress: ProgressCallback,
  ): Promise<AnalysisResult> {
    try {
      let finalAnalysis = {
        commit_analysis: {
          enabled: true,
          analysis: {
            owner: "Dave",
            repo: "Web",
            branch: "main",
            total_commits: 23,
            commits_analyzed: 23,
            analysis: {
              code_adequacy: 85,
              repo_adequacy: 90,
              ai: 70,
              fraud: 30,
              adequacy: 88,
              reasoning:
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eros turpis, varius et blandit eget, pulvinar ac mi. Etiam mauris erat, sagittis at gravida eget, mattis quis nulla. Cras ut convallis ante. Duis id sodales nunc. Nunc faucibus faucibus tortor et auctor. Aliquam erat volutpat. Integer et eleifend sapien, nec fringilla lorem. Etiam maximus lectus ut sagittis pulvinar. Integer sollicitudin dolor nec laoreet cursus. Suspendisse in ultrices mi. Nunc congue varius sapien.",
              red_flags: [],
              total_commits_analyzed: 23,
              total_commits_in_repo: 23,
            },
          },
          readme_analysis: {
            probability: 25,
            reasoning:
              "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eros turpis, varius et blandit eget, pulvinar ac mi. Etiam mauris erat, sagittis at gravida eget, mattis quis nulla. Cras ut convallis ante. Duis id sodales nunc. Nunc faucibus faucibus tortor et auctor. Aliquam erat volutpat. Integer et eleifend sapien, nec fringilla lorem. Etiam maximus lectus ut sagittis pulvinar. Integer sollicitudin dolor nec laoreet cursus. Suspendisse in ultrices mi. Nunc congue varius sapien.",
            summary:
              "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eros turpis, varius et blandit eget, pulvinar ac mi. Etiam mauris erat, sagittis at gravida eget, mattis quis nulla. Cras ut convallis ante. Duis id sodales nunc. Nunc faucibus faucibus tortor et auctor. Aliquam erat volutpat. Integer et eleifend sapien, nec fringilla lorem. Etiam maximus lectus ut sagittis pulvinar. Integer sollicitudin dolor nec laoreet cursus. Suspendisse in ultrices mi. Nunc congue varius sapien.",
            complexity: 60,
          },
        },
        som_analysis: {
          enabled: true,
          analysis: {
            project_id: 3939,
            devlogs_count: 7,
            ai_analysis: {
              devlogs_adequacy: 70,
              ai_devlogs: 30,
              fraud: 60,
              adequacy: 65,
              reasoning:
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eros turpis, varius et blandit eget, pulvinar ac mi. Etiam mauris erat, sagittis at gravida eget, mattis quis nulla. Cras ut convallis ante. Duis id sodales nunc. Nunc faucibus faucibus tortor et auctor. Aliquam erat volutpat. Integer et eleifend sapien, nec fringilla lorem. Etiam maximus lectus ut sagittis pulvinar. Integer sollicitudin dolor nec laoreet cursus. Suspendisse in ultrices mi. Nunc congue varius sapien.",
              red_flags: [],
              total_devlogs: 7,
            },
            total_time_coded: 0,
            readme_analysis: {
              probability: 35,
              reasoning:
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eros turpis, varius et blandit eget, pulvinar ac mi. Etiam mauris erat, sagittis at gravida eget, mattis quis nulla. Cras ut convallis ante. Duis id sodales nunc. Nunc faucibus faucibus tortor et auctor. Aliquam erat volutpat. Integer et eleifend sapien, nec fringilla lorem. Etiam maximus lectus ut sagittis pulvinar. Integer sollicitudin dolor nec laoreet cursus. Suspendisse in ultrices mi. Nunc congue varius sapien.",
              complexity: 60,
              summary:
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eros turpis, varius et blandit eget, pulvinar ac mi. Etiam mauris erat, sagittis at gravida eget, mattis quis nulla. Cras ut convallis ante. Duis id sodales nunc. Nunc faucibus faucibus tortor et auctor. Aliquam erat volutpat. Integer et eleifend sapien, nec fringilla lorem. Etiam maximus lectus ut sagittis pulvinar. Integer sollicitudin dolor nec laoreet cursus. Suspendisse in ultrices mi. Nunc congue varius sapien.",
            },
          },
        },
        repo_analysis: {
          enabled: true,
          analysis: {
            slopscore: 65,
            reasoning:
              "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eros turpis, varius et blandit eget, pulvinar ac mi. Etiam mauris erat, sagittis at gravida eget, mattis quis nulla. Cras ut convallis ante. Duis id sodales nunc. Nunc faucibus faucibus tortor et auctor. Aliquam erat volutpat. Integer et eleifend sapien, nec fringilla lorem. Etiam maximus lectus ut sagittis pulvinar. Integer sollicitudin dolor nec laoreet cursus. Suspendisse in ultrices mi. Nunc congue varius sapien.",
            main_factors: [
              "AI-assisted commits",
              "Time-inflation",
              "Devlog inconsistencies",
            ],
          },
        },
        code_analysis: {
          enabled: true,
          analysis: {
            total_files_analyzed: 11,
            code_features: [],
            ai_analysis: {
              total_files_analyzed: 11,
              analysis_results: {
                ai: 85,
                perfectness: 95,
                unused: 20,
                reasoning:
                  "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse eros turpis, varius et blandit eget, pulvinar ac mi. Etiam mauris erat, sagittis at gravida eget, mattis quis nulla. Cras ut convallis ante. Duis id sodales nunc. Nunc faucibus faucibus tortor et auctor. Aliquam erat volutpat. Integer et eleifend sapien, nec fringilla lorem. Etiam maximus lectus ut sagittis pulvinar. Integer sollicitudin dolor nec laoreet cursus. Suspendisse in ultrices mi. Nunc congue varius sapien.",
              },
            },
          },
        },
        code_score: {
          enabled: true,
        },
      };

      onProgress(5, "Starting analysis...");
      if (mode === "repo") {
        finalAnalysis.commit_analysis.enabled = true;
        finalAnalysis.som_analysis.enabled = true;
        finalAnalysis.repo_analysis.enabled = true;
        finalAnalysis.code_analysis.enabled = false;
        finalAnalysis.code_score.enabled = false;

        if (this.isSummerOfMakingUrl(url)) {
          const links = await this.getLinksFromSomProject(url);

          onProgress(25, "Analyzing github repo ...");
          await this.analyzeRepo(links.repo_link, onProgress, finalAnalysis);
          onProgress(50, "Analyzing SoM devlogs...");
          await this.analyzeSoMProject(url, onProgress, finalAnalysis);
        } else {
          onProgress(25, "Analyzing github repo ...");
          await this.analyzeRepo(url, onProgress, finalAnalysis);
          finalAnalysis.som_analysis.enabled = false;
        }
        console.log(finalAnalysis);
        onProgress(75, "Calculating SlopScore ...");
        await this.calculateSlopScore(
          finalAnalysis.commit_analysis.readme_analysis,
          finalAnalysis.commit_analysis.analysis,
          finalAnalysis.som_analysis.analysis,
          finalAnalysis,
        );
        onProgress(100, "Analysis complete!");
        console.log("Final Analysis:", finalAnalysis);

        return finalAnalysis;
      } else if (mode === "code") {
        finalAnalysis.commit_analysis.enabled = false;
        finalAnalysis.som_analysis.enabled = false;
        finalAnalysis.repo_analysis.enabled = false;
        finalAnalysis.code_analysis.enabled = true;
        finalAnalysis.code_score.enabled = true;

        if (this.isSummerOfMakingUrl(url)) {
          const links = await this.getLinksFromSomProject(url);

          onProgress(80, "Analyzing the code ...");
          await this.analyzeCode(links.repo_link, finalAnalysis);
        } else {
          onProgress(80, "Analyzing the code ...");
          await this.analyzeCode(url, finalAnalysis);
        }
        onProgress(75, "Calculating SlopScore ...");
        console.log(finalAnalysis);
        finalAnalysis.repo_analysis.analysis.slopscore =
            finalAnalysis.code_analysis.analysis.ai_analysis.analysis_results.ai;
        onProgress(100, "Analysis complete!");
        console.log("Final Analysis:", finalAnalysis);

        return finalAnalysis;
      } else if (mode === "both") {
        finalAnalysis.commit_analysis.enabled = true;
        finalAnalysis.som_analysis.enabled = true;
        finalAnalysis.repo_analysis.enabled = true;
        finalAnalysis.code_analysis.enabled = true;
        finalAnalysis.code_score.enabled = true;

        if (this.isSummerOfMakingUrl(url)) {
          const links = await this.getLinksFromSomProject(url);

          onProgress(20, "Analyzing github repo ...");
          await this.analyzeRepo(links.repo_link, onProgress, finalAnalysis);

          onProgress(40, "Analyzing SoM devlogs...");
          await this.analyzeSoMProject(url, onProgress, finalAnalysis);

          onProgress(60, "Calculating SlopScore ...");
          await this.calculateSlopScore(
            finalAnalysis.commit_analysis.readme_analysis,
            finalAnalysis.commit_analysis.analysis,
            finalAnalysis.som_analysis.analysis,
            finalAnalysis,
          );
          onProgress(80, "Analyzing the code ...");
          await this.analyzeCode(links.repo_link, finalAnalysis);
        } else {
          onProgress(20, "Analyzing github repo ...");
          await this.analyzeRepo(url, onProgress, finalAnalysis);

          onProgress(60, "Calculating SlopScore ...");
          await this.calculateSlopScore(
            finalAnalysis.commit_analysis.readme_analysis,
            finalAnalysis.commit_analysis.analysis,
            {},
            finalAnalysis,
          );
          onProgress(80, "Analyzing the code ...");
          await this.analyzeCode(url, finalAnalysis);
          finalAnalysis.som_analysis.enabled = false;
        }
        onProgress(100, "Analysis complete!");
        console.log("Final Analysis:", finalAnalysis);

        return finalAnalysis;
      }
    } catch (error) {
      throw error;
    }
  }

  async calculateSlopScore(
    readmeAnalysis: any,
    repoAnalysis: any,
    somAnalysis: any,
    finalAnalysis: any,
  ) {
    try {
      const response = await fetch(`${this.baseUrl}/repo-analysis`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          readme_analysis: readmeAnalysis,
          repo_analysis: repoAnalysis,
          som_analysis: somAnalysis,
        }),
      });

      if (!response.ok) {
        throw new Error(
          `Failed to calculate slop score: ${response.statusText}`,
        );
      }

      const slopScoreResult = await response.json();

      finalAnalysis.repo_analysis.analysis = slopScoreResult;
    } catch (error) {
      throw error;
    }
  }

  async analyzeCode(repo_url: string, final_analysis: any) {
    try {
      const formData = new FormData();

      formData.append("repo_url", repo_url);

      const response = await fetch(
        `${this.baseUrl}/code-analysis?repo_url=${encodeURIComponent(repo_url)}`,
        {
          method: "GET",
        },
      );

      if (!response.ok) {
        throw new Error(`Failed to analyze code: ${response.statusText}`);
      }

      const codeAnalysisResult = await response.json();

      final_analysis.code_analysis.analysis = codeAnalysisResult;
    } catch (error) {
      throw error;
    }
  }

  private async analyzeRepo(
    repoUrl: string,
    onProgress: ProgressCallback,
    finalAnalysis: any,
  ) {
    let readmeAnalysis: ReadmeAnalysis | undefined;
    let commitAnalysis: CommitAnalysis | undefined;

    try {
      const readmeResponse = await fetch(
        `${this.baseUrl}/repo-analysis/readme-analysis?repo_url=${encodeURIComponent(repoUrl)}`,
      );

      if (readmeResponse.ok) {
        const readmeData = await readmeResponse.json();

        readmeAnalysis = {
          probability: readmeData.probability || 0,
          reasoning: readmeData.reasoning || "",
          summary: readmeData.summary || "",
          complexity: readmeData.complexity || "",
        };
      }
    } catch (error) {
      throw error;
    }

    try {
      const commitResponse = await fetch(
        `${this.baseUrl}/repo-analysis/commits-analysis?repo_url=${encodeURIComponent(repoUrl)}`,
      );

      if (commitResponse.ok) {
        const commitAnalysis = await commitResponse.json();

        finalAnalysis.commit_analysis.analysis = commitAnalysis;
      }
    } catch (error) {
      throw error;
    }

    finalAnalysis.commit_analysis.readme_analysis = readmeAnalysis;
  }

  private async analyzeSoMProject(
    projectUrl: string,
    onProgress: ProgressCallback,
    finalAnalysis: any,
  ) {
    try {
      const somResponse = await fetch(
        `${this.baseUrl}/som-analysis?project=${encodeURIComponent(projectUrl)}`,
      );

      if (!somResponse.ok) {
        throw new Error("Failed to fetch Summer of Making project");
      }

      const somData = await somResponse.json();

      finalAnalysis.som_analysis.analysis = somData;
    } catch (error) {
      throw error;
    }
  }

  private formatGitHubResults(
    readmeAnalysis?: ReadmeAnalysis,
    commitAnalysis?: CommitAnalysis,
    codeFeatures?: CodeFeatures[],
    codeAnalysisResult?: CodeAnalysisResult,
    slopScoreResult?: SlopScoreResult,
  ): AnalysisResult {
    const repoScore =
      slopScoreResult?.individual_scores?.repo_score ||
      commitAnalysis?.authenticity_score ||
      Math.random() * 100;

    const codeScore =
      slopScoreResult?.individual_scores?.code_score ||
      codeAnalysisResult?.code_quality_score ||
      Math.random() * 100;

    const overallScore =
      slopScoreResult?.slopscore || (repoScore + codeScore) / 2;

    return {
      repoAnalysis: {
        aiUsage: readmeAnalysis?.probability || 0,
        commits: commitAnalysis?.time_analysis?.total_commits || 0,
        adequacy: commitAnalysis?.authenticity_score || 0,
        readmeAnalysis,
        commitAnalysis,
      },
      somAnalysis: {
        devlogs: 0,
        avgTime: "0h",
        authenticity: 0,
      },
      codeAnalysis: {
        aiInCode: codeAnalysisResult?.ai_usage_probability || 0,
        perfectness: codeAnalysisResult?.code_quality_score || 0,
        unusedCode: 0, // This would need additional analysis
        features: codeFeatures,
        analysis: codeAnalysisResult,
      },
      repoSlopScore: Math.round(repoScore),
      codeSlopScore: Math.round(codeScore),
      overallSlopScore: Math.round(overallScore),
      repoInsights: [
        ...(commitAnalysis?.slop_indicators || []),
        ...(readmeAnalysis?.reasoning ? [readmeAnalysis.reasoning] : []),
      ],
      codeInsights: codeAnalysisResult?.slop_indicators || [],
      detailedAnalysis: {
        repo:
          slopScoreResult?.reasoning ||
          commitAnalysis?.development_pattern ||
          "Repository analysis completed",
        code:
          codeAnalysisResult?.detailed_analysis || "Code analysis completed",
      },
      slopScoreAnalysis: slopScoreResult,
    };
  }

  private formatSummerResults(somData: any): AnalysisResult {
    const analysis = somData.ai_analysis;
    const repoAnalysis = somData.readme_analysis;

    return {
      repoAnalysis: {
        aiUsage: repoAnalysis?.probability || 0,
        commits: 0,
        adequacy: analysis?.authenticity_score || 0,
      },
      somAnalysis: {
        devlogs: somData.devlogs_count || 0,
        avgTime: this.formatCodingTime(somData.total_time_coded),
        authenticity: analysis?.authenticity_score || 0,
        analysis,
      },
      codeAnalysis: {
        aiInCode: 0,
        perfectness: 0,
        unusedCode: 0,
      },
      repoSlopScore: Math.round(analysis?.authenticity_score || 0),
      codeSlopScore: 0,
      overallSlopScore: Math.round(analysis?.authenticity_score || 0),
      repoInsights: analysis?.slop_indicators || [],
      codeInsights: [],
      detailedAnalysis: {
        repo:
          analysis?.development_pattern?.summary ||
          "Summer of Making project analyzed",
        code: "No code analysis for Summer of Making projects",
      },
    };
  }

  private formatCodingTime(totalSeconds?: number): string {
    if (!totalSeconds) return "0h";

    const hours = Math.floor(totalSeconds / 3600);
    const minutes = Math.floor((totalSeconds % 3600) / 60);

    if (hours > 0) {
      return `${hours}h ${minutes > 0 ? `${minutes}m` : ""}`.trim();
    }

    return `${minutes}m`;
  }

  // Keep the mock method for testing
  async mockAnalyzeRepository(
    url: string,
    options: {
      mode: "both" | "repo" | "code";
      maxFiles: number;
    },
    onProgress: ProgressCallback,
  ): Promise<AnalysisResult> {
    const steps = [
      { progress: 10, status: "Initializing analysis..." },
      { progress: 20, status: "Fetching repository information..." },
      { progress: 30, status: "Cloning repository..." },
      { progress: 40, status: "Analyzing commit history..." },
      { progress: 60, status: "Analyzing code structure..." },
      { progress: 80, status: "Generating insights..." },
      { progress: 95, status: "Finalizing results..." },
      { progress: 100, status: "Analysis complete!" },
    ];

    for (const step of steps) {
      onProgress(step.progress, step.status);
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    // Return mock data
    return {
      repoAnalysis: {
        aiUsage: Math.floor(Math.random() * 30),
        commits: Math.floor(Math.random() * 500) + 50,
        adequacy: Math.floor(Math.random() * 100),
      },
      somAnalysis: {
        devlogs: Math.floor(Math.random() * 50) + 5,
        avgTime: `${(Math.random() * 8 + 1).toFixed(1)}h`,
        authenticity: Math.floor(Math.random() * 100),
      },
      codeAnalysis: {
        aiInCode: Math.floor(Math.random() * 20),
        perfectness: Math.floor(Math.random() * 100),
        unusedCode: Math.floor(Math.random() * 40),
      },
      repoSlopScore: Math.floor(Math.random() * 100),
      codeSlopScore: Math.floor(Math.random() * 100),
      overallSlopScore: Math.floor(Math.random() * 100),
      repoInsights: ["Vague commits", "AI in README", "Good devlogs"],
      codeInsights: ["Clean structure", "Some duplicates", "Good performance"],
      detailedAnalysis: {
        repo: "The repository shows signs of AI-generated content in the README and commit messages. However, the project structure is well-organized and the development logs indicate genuine effort and learning.",
        code: "The codebase demonstrates good architectural patterns with minimal code duplication. Some functions show characteristics of AI assistance, but the overall implementation is sound and performant.",
      },
    };
  }
}

export const analysisService = new AnalysisService();
export type { AnalysisResult };
