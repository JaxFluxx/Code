package comparator;

import java.util.Arrays;

public class StringTest
{

	public static void main(String[] args)
	{
		String[] sArr=new String[] {"China","America","France","Switzerland "};
		Arrays.sort(sArr, new LengthComparator());
		for(String s:sArr)
			System.out.println(s);
		Arrays.sort(sArr);
		for(String s:sArr)
			System.out.println(s);
	}

}
