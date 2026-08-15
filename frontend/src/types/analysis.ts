export interface SkillGap {
  skill: string;
  priority: 'high' | 'medium' | 'low';
  reason: string;
}

export interface RoadmapItem {
  day: number;
  topic: string;
  priority: 'high' | 'medium' | 'low';
  activity: string;
  effort: string;
  reason: string;
}

export interface InterviewQuestion {
  category: 'technical' | 'resume' | 'behavioral' | 'job-specific';
  question: string;
  hint?: string;
}

export interface InterviewEvaluation {
  overall_score: number;
  relevance_score: number;
  technical_score: number;
  clarity_score: number;
  completeness_score: number;
  strengths: string[];
  missing_points: string[];
  improvement_tips: string[];
  suggested_better_answer: string;
  final_feedback: string;
}

export interface AnalysisResult {
  match_score: number;
  match_category: string;
  summary: string;
  matching_skills: string[];
  skill_gaps: SkillGap[];
  strengths: string[];
  weaknesses: string[];
  important_requirements: string[];
  priority_gaps: SkillGap[];
  learning_roadmap: RoadmapItem[];
  interview_questions: InterviewQuestion[];
}
