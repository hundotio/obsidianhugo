import os
import re
import shutil
import subprocess
from pathlib import Path

def findActive(obsidianBlogs):
    for blog in Path(obsidianBlogs).glob("*.md"):
        with open (blog, 'r') as file:
            content = file.read()
            if 'status: active' in content:
                print("Active blog " + blog.name + " found!\n")
                return blog
    print("No active blog found.")
    return None

def parseImages(activeBlog):
    with open(activeBlog, 'r') as file:
        content = file.read()
    images = re.findall(r'!\[\[(.*?)\]\]', content)
    return images

def copyImages(imageLinks, obsidianImages, hugoImages):
    for link in imageLinks:
        imagePath = os.path.join(obsidianImages, link)
        if os.path.exists(imagePath):
            shutil.copy(imagePath, hugoImages)
            print("Copied " + link + " into Hugo images directory!")
        else:
            print("Image " + link + " not found.")
    print()

def copyBlog(activeBlog, obsidianBlogs, hugoBlogs):
    obsidianBlogs = Path(obsidianBlogs).expanduser()
    hugoBlogs = Path(hugoBlogs).expanduser()
    activeBlog = Path(activeBlog).expanduser()

    directories = [d for d in hugoBlogs.iterdir() if d.is_dir()]
    if not directories:
            print("No hugo blog topics found.")
            return None
    
    for idx, directory in enumerate(directories, start=1):
            print(f"{idx}. {directory.name}")
    
    while True:
        try:
            choice = int(input("Select a blog topic: ").strip())
            if 1 <= choice <= len(directories):
                selected_directory = directories[choice - 1]
                break
            else:
                print("Invalid choice.")
        except ValueError:
            print("Invalid input.")

    hugoFinal = hugoBlogs / selected_directory.name
    print(hugoFinal)

    shutil.copy(activeBlog, hugoFinal)
    print("Copied active blog into Hugo blogs directory! \n")

    return hugoFinal

def publishBlog(githubPath):
    repoDir = Path(githubPath).expanduser()

    if not repoDir.exists() or not repoDir.is_dir():
        raise ValueError(f"Invalid repository directory: {repoDir}")

    commitMessage = input("Enter a commit message: ").strip()

    if not commitMessage:
        print("Commit message cannot be empty.")
        return

    subprocess.run(["git", "add", "."], cwd=repoDir)
    subprocess.run(["git", "commit", "-m", commitMessage], cwd=repoDir)
    subprocess.run(["git", "push"], cwd=repoDir)

    print()
    print("Blogpost published!")

def updateLinks(hugoFinal, activeBlog):
    finalBlog = hugoFinal / activeBlog.name
    with open(finalBlog, 'r') as file:
        content = file.read()

    pattern = r'!\[\[(.*?)\]\]'

    def replace_link(match):
        file_name = match.group(1)
        return f'![{file_name}](/images/{file_name})'
    
    updated_content = re.sub(pattern, replace_link, content)

    with open(finalBlog, 'w') as file:
        file.write(updated_content)

    print(f"Updated Obsidian links in {finalBlog} to Hugo format.")

def main():    
    # Explicit paths for Obsidian and Hugo
    obsidianBlogs="/full/path/to/obsidian/blogs"
    obsidianImages="/full/path/to/obsidian/images"
    hugoBlogs="/full/path/to/hugo/blogs"
    hugoImages="/full/path/to/hugo/images"
    githubPath="/full/path/to/hugo/site"
 
    # Parse markdown frontmatter and find active status
    activeBlog = findActive(obsidianBlogs)

    # Move post into Hugo blog directory
    hugoFinal = copyBlog(activeBlog, obsidianBlogs, hugoBlogs)

    # Parse photo links in file
    imageLinks = parseImages(activeBlog)

    # Update image links in copied blogpost
    updateLinks(hugoFinal, activeBlog)

    # Copy images into Hugo static directory
    copyImages(imageLinks, obsidianImages, hugoImages)

    # Push to GitHub
    publishBlog(githubPath)

if __name__ == "__main__":
    main()