# Palabam User Guide

## For Teachers

### Getting Started

1. **Sign Up**: Create a teacher account at `/signup/teacher`
2. **Create Classes**: Click "Create Class" on your dashboard to set up classes
3. **Invite Students**: Use the "Send Invites" page to generate invite links or send email invites
4. **Share Invite Links**: Students use these links to join your class

### Uploading Student Transcripts

1. Navigate to **Upload Transcript** (`/upload`)
2. Select a **Class** from the dropdown
3. Select a **Student** from that class
4. Paste or type the student's transcript in the text area (minimum 10 words)
5. Click **Analyze Transcript**

The system will:
- Analyze the transcript for vocabulary patterns
- Calculate the student's vocabulary level
- Generate 5-7 personalized word recommendations
- Store the profile in the database
- Display results immediately

### Viewing Student Progress

**Dashboard View** (`/dashboard`):
- See all students across all your classes
- View latest vocabulary level for each student
- See number of recommended words
- Check last profile date
- Expand any student to see their recommendations and profile history

**Student Detail View** (`/students/{id}`):
- Complete vocabulary profile
- All recommended words with definitions and examples
- Full profile history timeline
- Export options (CSV/PDF)

### Managing Invites

Navigate to **Send Invites** (`/teacher/invites`):

**Email Invites**:
1. Select a class
2. Enter student email addresses (one per line)
3. Click "Send Invites"
4. Students receive email with invite link

**Shareable Links**:
1. Select a class
2. Click "Generate Link"
3. Copy and share the link with students
4. Link can be reused for multiple students in the same class

### Exporting Data

**From Dashboard**:
- Click **CSV** or **PDF** buttons in the header
- Exports all students' recommendations

**From Student Detail**:
- Click **Export CSV** or **Export PDF** buttons
- Exports that specific student's recommendations

## For Students

### Getting Started

1. **Receive Invite**: Get an invite link from your teacher (via email or shared link)
2. **Join Class**: Click the invite link and sign up with your email and name
3. **Verify Email**: Check your email for the magic link to complete signup
4. **Start Creating**: Use Story Spark to create transcripts

### Using Story Spark

1. Navigate to **Story Spark** (`/story-spark`)
2. Read the story prompt
3. Choose **Text Mode** or **Voice Mode**:
   - **Text Mode**: Type your story
   - **Voice Mode**: Click the microphone to record
4. Tell your story (minimum 10 words)
5. Click **Submit Story**

You'll immediately see:
- Your vocabulary level
- Recommended words to learn
- Word definitions and examples
- Your progress

### Viewing Your Progress

Navigate to **Student Dashboard** (`/student/dashboard`):
- See your vocabulary level
- View recommended words
- Track your progress over time
- See your profile history

## For Parents

### Getting Started

1. **Sign Up**: Create a parent account at `/signup/parent`
2. **Link Children**: During signup or after, link to your children's existing student accounts using their email
3. **View Dashboard**: Access your parent dashboard to see all your children's progress

### Parent Dashboard

Navigate to **Parent Dashboard** (`/parent/dashboard`):
- See all your children listed
- View each child's:
  - Latest vocabulary level
  - Number of recommended words
  - Last profile date
  - Progress summary
- Click on any child to see detailed progress

### Child Detail View

Click on a child to see:
- Complete vocabulary profile
- All recommended words
- Profile history timeline
- Progress metrics

## Workflows

### Teacher Workflow: Analyze Student Work

1. Teacher uploads student transcript → `/upload`
2. System analyzes and creates profile
3. Recommendations generated automatically
4. Teacher views results on dashboard
5. Teacher can export data for planning

### Student Workflow: Create and Learn

1. Student receives invite link from teacher
2. Student signs up via invite link
3. Student creates transcript in Story Spark
4. Student sees immediate feedback and recommendations
5. Student can track progress over time

### Parent Workflow: Monitor Progress

1. Parent signs up and links to children's accounts
2. Parent views dashboard with all children
3. Parent clicks child to see detailed progress
4. Parent can see vocabulary recommendations and history

## Tips

### For Teachers

- **Regular Analysis**: Upload new transcripts periodically to track student growth
- **Use Recommendations**: The recommended words are personalized to each student's ZPD (Zone of Proximal Development)
- **Export for Planning**: Use CSV/PDF exports to plan vocabulary instruction
- **Class Organization**: Create separate classes for different grade levels or subjects

### For Students

- **Be Creative**: Story Spark prompts are designed to encourage creative expression
- **Use New Words**: Try to use the recommended words in future stories
- **Track Progress**: Check your dashboard regularly to see vocabulary growth
- **Practice**: The more you write, the better the system understands your vocabulary level

### For Parents

- **Regular Check-ins**: Review your children's progress regularly
- **Encourage Writing**: Support your children in using Story Spark regularly
- **Discuss Words**: Talk about the recommended words with your children
- **Celebrate Growth**: Watch vocabulary levels improve over time

## Troubleshooting

### "No students found"
- Make sure you've created classes and students have joined
- Check that students have accepted their invites

### "Failed to analyze transcript"
- Ensure transcript is at least 10 words
- Check your internet connection
- Try again - the system may be processing

### "Can't link to student"
- Verify the student email is correct
- Ensure the student has already signed up
- Students must exist before parents can link

### Export not working
- Check browser permissions for downloads
- Try a different browser
- Ensure you have data to export

## Support

For technical issues or questions, contact your teacher or administrator.

