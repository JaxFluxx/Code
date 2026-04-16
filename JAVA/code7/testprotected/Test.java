package testprotected;

import java.util.ArrayList;
import java.util.Arrays;

class Person
{
	private String name;
	private int age;

	public Person() {}
	public Person(String name, int age)
	{
		this.name = name;
		this.age = age;
		
	}
	protected String getName()
	{
		return name;
		
	}
	public static void main(String[] args) throws CloneNotSupportedException
	{
		Person p1=new Person();
		p1.clone();
		
	}
}

public class Test 
{
	public static void main(String[] args) throws CloneNotSupportedException
	{
		Person p1=new Person();
		p1.getName();
//		p1.clone();
		Test t1=new Test();
		t1.clone();
	}
}