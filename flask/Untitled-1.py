message = """
**Make Your Mark:** Embrace the opportunity to leave your indelible mark on the world through ground-breaking research, innovative technologies, and impactful discoveries. 
**Join a Thriving Community:** Connect with a network of brilliant and passionate women in STEM, fostering collaboration, mentorship, and mutual support. 
**Inspire the Next Generation:** Serve as a role model for younger girls and women, encouraging them to pursue their dreams in STEM fields and break down gender barriers. 
**Challenge Stereotypes:** Shatter the misconception that STEM is exclusively a male domain. Demonstrate your capabilities, defy expectations, and pave the way for future generations. 
**Advocate for Change:** Be an advocate for gender equality in STEM, both in your workplace and beyond. Speak up against bias, discrimination, and unfair treatment, and work towards creating a more inclusive environment. 
**Embrace Continuous Learning:** Embrace ongoing learning and skill development to stay at the forefront of your field. Attend conferences, webinars, and workshops, and engage in online courses to enhance your knowledge and expertise. 
**Networking is Key:** Attend industry events, conferences, and workshops to expand your professional network, connect with potential collaborators, and learn about the latest advancements in your field. 
**Mentorship Matters:** Seek out mentors and sponsors who can provide guidance, support, and insights throughout your career. Offer mentorship to younger women in STEM, paying it forward and fostering a supportive community. 
**Don't Fear Failure:** Remember that failure is a natural part of the learning and innovation process. Embrace setbacks as opportunities for growth, and persevere in the face of challenges. 
**Be a Role Model:** By excelling in your field, you become a role model for other women in STEM. Showcase your achievements, share your experiences, and encourage others to pursue their passions in science, technology, engineering, and mathematics.
"""

formatted_message = ""
lines = message.split("\n")

for line in lines:
    bold_text = ""
    while "**" in line:
        start_index = line.index("**")
        end_index = line.index("**", start_index + 2)
        bold_text += "<strong>" + line[start_index + 2:end_index] + "</strong>"
        line = line[:start_index] + bold_text + line[end_index + 2:]
    formatted_message += line + "<br>"

# Writing the formatted message to a text file
with open("formatted_message.html", "w") as file:
    file.write(formatted_message)

print("Formatted message has been written to formatted_message.html")
