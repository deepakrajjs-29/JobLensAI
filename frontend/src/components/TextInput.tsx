interface TextInputProps {
  value: string;
  onChange: (value: string) => void;
}

export default function TextInput({ value, onChange }: TextInputProps) {
  return (
    <textarea
      className="jd-textarea"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      placeholder="Paste the full job description here...&#10;&#10;Include the job title, responsibilities, required qualifications, preferred skills, and any other relevant details."
      aria-label="Job Description text input"
    />
  );
}
