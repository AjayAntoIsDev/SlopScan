interface AnalysisResult {
  repoAnalysis: {
    aiUsage: number;
    commits: number;
    adequacy: number;
  };
  somAnalysis: {
    devlogs: number;
    avgTime: string;
    authenticity: number;
  };
  codeAnalysis: {
    aiInCode: number;
    perfectness: number;
    unusedCode: number;
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
}

interface ProgressCallback {
  (progress: number, status: string): void;
}

class AnalysisService {
  private baseUrl = "http://localhost:8000";
  async analyzeRepository(
    url: string,
    options: {
      mode: "both" | "repo" | "code";
      maxFiles: number;
    },
    onProgress: ProgressCallback,
  ): Promise<AnalysisResult> {
    try {
      // Step 1: Initialize analysis
      onProgress(10, "Initializing analysis...");

      const initResponse = await fetch(`${this.baseUrl}/api/analyze/init`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          url,
          mode: options.mode,
          maxFiles: options.maxFiles,
        }),
      });

      if (!initResponse.ok) {
        throw new Error("Failed to initialize analysis");
      }

      const { sessionId } = await initResponse.json();

      onProgress(20, "Fetching repository information...");

      // Step 2: Start analysis and poll for progress
      const analyzeResponse = await fetch(`${this.baseUrl}/api/analyze/start`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ sessionId }),
      });

      if (!analyzeResponse.ok) {
        throw new Error("Failed to start analysis");
      }

      // Step 3: Poll for progress
      return await this.pollForResults(sessionId, onProgress);
    } catch (error) {
      console.error("Analysis failed:", error);
      throw error;
    }
  }

  private async pollForResults(
    sessionId: string,
    onProgress: ProgressCallback,
  ): Promise<AnalysisResult> {
    const maxAttempts = 60; // 5 minutes max (5 second intervals)
    let attempts = 0;

    while (attempts < maxAttempts) {
      try {
        const response = await fetch(
          `${this.baseUrl}/api/analyze/status/${sessionId}`,
        );

        if (!response.ok) {
          throw new Error("Failed to get analysis status");
        }

        const data = await response.json();

        // Update progress based on status
        switch (data.status) {
          case "fetching_repo":
            onProgress(30, "Cloning repository...");
            break;
          case "analyzing_commits":
            onProgress(40, "Analyzing commit history...");
            break;
          case "analyzing_code":
            onProgress(60, "Analyzing code structure...");
            break;
          case "generating_insights":
            onProgress(80, "Generating insights...");
            break;
          case "finalizing":
            onProgress(95, "Finalizing results...");
            break;
          case "completed":
            onProgress(100, "Analysis complete!");

            return this.formatResults(data.results);
          case "error":
            throw new Error(data.error || "Analysis failed");
        }

        // Wait before next poll
        await new Promise((resolve) => setTimeout(resolve, 5000));
        attempts++;
      } catch (error) {
        console.error("Polling error:", error);
        attempts++;

        if (attempts >= maxAttempts) {
          throw new Error("Analysis timeout");
        }

        await new Promise((resolve) => setTimeout(resolve, 5000));
      }
    }

    throw new Error("Analysis timeout");
  }

  private formatResults(results: any): AnalysisResult {
    // Format the raw API results into our expected structure
    return {
      repoAnalysis: {
        aiUsage: results.repo_analysis?.ai_usage || 0,
        commits: results.repo_analysis?.commit_count || 0,
        adequacy: results.repo_analysis?.adequacy_score || 0,
      },
      somAnalysis: {
        devlogs: results.som_analysis?.devlog_count || 0,
        avgTime: results.som_analysis?.avg_time || "0h",
        authenticity: results.som_analysis?.authenticity_score || 0,
      },
      codeAnalysis: {
        aiInCode: results.code_analysis?.ai_in_code || 0,
        perfectness: results.code_analysis?.perfectness_score || 0,
        unusedCode: results.code_analysis?.unused_code_percentage || 0,
      },
      repoSlopScore: results.scores?.repo_slop_score || 0,
      codeSlopScore: results.scores?.code_slop_score || 0,
      overallSlopScore: results.scores?.overall_slop_score || 0,
      repoInsights: results.insights?.repo_insights || [],
      codeInsights: results.insights?.code_insights || [],
      detailedAnalysis: {
        repo: results.detailed_analysis?.repo_analysis || "",
        code: results.detailed_analysis?.code_analysis || "",
      },
    };
  }

  // Fallback method for testing without backend
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
