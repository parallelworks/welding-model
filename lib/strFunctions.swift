# Convert a string to a boolean
(boolean result) str2bool (string strIn){
   string strInLower = toLower(strIn);
   result = matches(strInLower,"yes") || matches(strInLower,"y") || matches(strInLower,"true") || matches(strInLower,"t") || matches(strInLower,"1");
}

# Trim a suffix from a file path: basically trim anything after the last "." in the string
(string nameNoSuffix) trimSuffix (string nameWithSuffix){
   int suffixStartLoc = lastIndexOf(nameWithSuffix, ".", -1);
   nameNoSuffix = substring(nameWithSuffix, 0, suffixStartLoc);
}
