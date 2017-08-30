import os
import zipfile

exclude_dirs = set([
".git", 
"__pycache__",
"doc",
"release"
])

exclude_files = set([
"create_version",	
".gitignore",
".pyc",
".sublime-workspace",
".sublime-project",
])


def WriteDirectoryToZipFile( zipHandle, srcPath, zipLocalPath = "", zipOperation = zipfile.ZIP_DEFLATED ):
	basePath = os.path.split( srcPath )[ 0 ]	
	for root, dirs, files in os.walk( srcPath ):
		
		dirs[:] = [d for d in dirs if d not in exclude_dirs]
		p = os.path.join( zipLocalPath, root [ ( len( basePath ) + 1 ) : ] )
		# add dir
		
		#if p == os.path.split(root)[1]:
		#	p = ""

		zipHandle.write( root, p, zipOperation )
		# add files
		for f in files:
				
				base, ext = os.path.splitext(f)
				#print(base, ext)
				if ext in exclude_files or base in exclude_files:
					continue
	
				filePath = os.path.join( root, f )
				fileInZipPath = os.path.join( p, f )
				zipHandle.write( filePath, fileInZipPath, zipOperation )

def main():
	zf = zipfile.ZipFile("./release/workplane.zip", "w")
	WriteDirectoryToZipFile(zf, os.path.split(__file__)[0])
	zf.close()


if __name__ == '__main__':
	main()
