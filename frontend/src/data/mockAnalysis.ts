import type { AnalysisResult } from '../types/analysis';

export const mockAnalysis: AnalysisResult = {
  match_score: 82,
  match_category: 'Strong Match',
  summary:
    'Your resume demonstrates strong alignment with this Full-Stack Developer position. You have solid experience with React, TypeScript, and Node.js which are core requirements. However, there are notable gaps in cloud infrastructure (AWS) and CI/CD practices that should be addressed to strengthen your candidacy.',

  matching_skills: [
    'React',
    'TypeScript',
    'JavaScript',
    'Node.js',
    'REST APIs',
    'Git & GitHub',
    'PostgreSQL',
    'Responsive Design',
  ],

  skill_gaps: [
    {
      skill: 'AWS (Lambda, S3, EC2)',
      priority: 'high',
      reason:
        'The job requires hands-on AWS experience for deploying and managing cloud infrastructure. Your resume does not mention AWS services.',
    },
    {
      skill: 'Docker & Containerization',
      priority: 'high',
      reason:
        'Container-based deployment is listed as a core requirement. No evidence of Docker experience in your resume.',
    },
    {
      skill: 'CI/CD Pipelines',
      priority: 'medium',
      reason:
        'The role expects experience with automated deployment pipelines. Your resume does not mention CI/CD tools like GitHub Actions or Jenkins.',
    },
    {
      skill: 'GraphQL',
      priority: 'medium',
      reason:
        'GraphQL is listed as a preferred skill. Your resume only shows REST API experience.',
    },
    {
      skill: 'Redis / Caching',
      priority: 'low',
      reason:
        'Caching strategies are mentioned as nice-to-have. Consider adding if time permits.',
    },
  ],

  strengths: [
    'Strong frontend development skills with React and TypeScript demonstrated through multiple projects',
    'Solid understanding of RESTful API design and backend development with Node.js',
    'Experience with relational databases (PostgreSQL) including schema design',
    'Good collaboration experience shown through open-source contributions and team projects',
  ],

  weaknesses: [
    'No demonstrated cloud infrastructure or DevOps experience',
    'Resume lacks quantifiable impact metrics for past projects',
    'No mention of testing practices (unit testing, integration testing)',
  ],

  important_requirements: [
    '3+ years of full-stack development experience',
    'Proficiency in React and TypeScript',
    'Experience with cloud services (AWS preferred)',
    'Understanding of CI/CD and DevOps practices',
    'Experience with containerized deployments',
    'Strong communication and collaboration skills',
  ],

  priority_gaps: [
    {
      skill: 'AWS (Lambda, S3, EC2)',
      priority: 'high',
      reason:
        'Critical requirement — mentioned 4 times in the job description. Immediate action recommended.',
    },
    {
      skill: 'Docker & Containerization',
      priority: 'high',
      reason:
        'Core infrastructure requirement. Needed for the deployment workflow described in the role.',
    },
    {
      skill: 'CI/CD Pipelines',
      priority: 'medium',
      reason:
        'Important for the team workflow. Can be learned relatively quickly with existing Git knowledge.',
    },
  ],

  learning_roadmap: [
    {
      day: 1,
      topic: 'AWS Fundamentals',
      priority: 'high',
      activity:
        'Complete AWS Cloud Practitioner essentials. Set up a free-tier account and deploy a simple Lambda function.',
      effort: '3–4 hours',
      reason:
        'AWS is the highest-priority gap and is mentioned as a core requirement in the job description.',
    },
    {
      day: 2,
      topic: 'Docker Basics',
      priority: 'high',
      activity:
        'Install Docker, containerize one of your existing Node.js projects. Learn Dockerfile, docker-compose basics.',
      effort: '3–4 hours',
      reason:
        'Containerization is required for the deployment workflow at this company.',
    },
    {
      day: 3,
      topic: 'CI/CD with GitHub Actions',
      priority: 'medium',
      activity:
        'Create a GitHub Actions pipeline for your containerized project. Automate testing and deployment.',
      effort: '2–3 hours',
      reason:
        'CI/CD connects your existing Git skills with the DevOps practices this role requires.',
    },
    {
      day: 4,
      topic: 'AWS S3 + Lambda Deep Dive',
      priority: 'high',
      activity:
        'Build a small project using S3 for storage and Lambda for backend logic. Practice with API Gateway.',
      effort: '3–4 hours',
      reason:
        'Hands-on AWS project experience will be directly relevant to interview discussions.',
    },
    {
      day: 5,
      topic: 'Mock Interview & Resume Update',
      priority: 'high',
      activity:
        'Practice answering technical and behavioral questions. Update your resume to include new AWS and Docker skills.',
      effort: '2–3 hours',
      reason:
        'Consolidate your preparation and ensure your resume reflects your updated skill set.',
    },
  ],

  interview_questions: [
    {
      category: 'technical',
      question:
        'Explain how you would design a RESTful API for a user management system. What endpoints would you create and why?',
      hint: 'Focus on CRUD operations, authentication, and proper HTTP methods.',
    },
    {
      category: 'technical',
      question:
        'What is the difference between server-side rendering and client-side rendering in React? When would you use each?',
      hint: 'Discuss performance, SEO, and user experience trade-offs.',
    },
    {
      category: 'technical',
      question:
        'How would you optimize a React application that is rendering slowly with a large dataset?',
      hint: 'Consider virtualization, memoization, pagination, and code splitting.',
    },
    {
      category: 'resume',
      question:
        'Tell me about the most challenging project on your resume. What was your specific contribution?',
      hint: 'Use the STAR method: Situation, Task, Action, Result.',
    },
    {
      category: 'resume',
      question:
        'I see you have experience with PostgreSQL. Can you walk me through how you designed the database schema for your project?',
      hint: 'Discuss normalization, relationships, indexes, and query optimization.',
    },
    {
      category: 'resume',
      question:
        'Your resume mentions open-source contributions. What did you learn from contributing to those projects?',
      hint: 'Highlight code review, collaboration, and coding standards.',
    },
    {
      category: 'behavioral',
      question:
        'Describe a time when you had to learn a new technology quickly to meet a deadline. How did you approach it?',
      hint: 'Show your learning process, resourcefulness, and time management.',
    },
    {
      category: 'behavioral',
      question:
        'Tell me about a time you disagreed with a teammate on a technical approach. How did you resolve it?',
      hint: 'Demonstrate communication, empathy, and willingness to compromise.',
    },
    {
      category: 'behavioral',
      question:
        'How do you prioritize tasks when you have multiple deadlines approaching simultaneously?',
      hint: 'Discuss your prioritization framework and communication with stakeholders.',
    },
    {
      category: 'job-specific',
      question:
        'This role requires deploying applications to AWS. While you may be learning AWS, how would you approach deploying a Node.js application to the cloud?',
      hint: 'Discuss EC2, Lambda, or container-based options even at a conceptual level.',
    },
    {
      category: 'job-specific',
      question:
        'How would you set up a CI/CD pipeline for a React + Node.js application? Walk me through the stages.',
      hint: 'Cover build, test, lint, deploy stages and mention specific tools.',
    },
    {
      category: 'job-specific',
      question:
        'What strategies would you use to ensure the reliability of a production web application?',
      hint: 'Discuss monitoring, logging, error handling, testing, and rollback strategies.',
    },
  ],
};
